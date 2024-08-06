from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from forms import LoginForm, SearchForm, RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import User, db, bcrypt, Exercises, UserExercise, WeeklyWorkout
import cv2
import numpy as np
import mediapipe as mp



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)


def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Middle point (vertex)
    c = np.array(c)  # Third point

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def gen_frames():
    print("gen_frames called")  # Debugging: Check if the function is called

    camera = cv2.VideoCapture(0)  # Use 0 for web camera

    if not camera.isOpened():
        print("Error: Camera could not be opened.")
        return

    import mediapipe as mp
    import numpy as np

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Initialize MediaPipe Pose
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            success, frame = camera.read()
            print("Reading frame")  # Debugging: Check if the camera frame is being read

            if not success:
                print("Failed to read frame from camera.")
                break
            else:
                # Convert the BGR image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Process the image and detect pose
                results = pose.process(image)

                # Convert the image color back to BGR for OpenCV
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                try:
                    # Extract landmarks
                    landmarks = results.pose_landmarks.landmark
                    torso = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

                    # Calculate the vectors
                    vector1 = np.array(shoulder) - np.array(torso)  # Vector from torso to shoulder
                    vector2 = np.array(elbow) - np.array(shoulder)  # Vector from shoulder to elbow

                    # Calculate the angle between the vectors
                    def calculate_angle(v1, v2):
                        v1 = np.array(v1)
                        v2 = np.array(v2)

                        dot_product = np.dot(v1, v2)
                        norm_v1 = np.linalg.norm(v1)
                        norm_v2 = np.linalg.norm(v2)
                        cos_angle = dot_product / (norm_v1 * norm_v2)
                        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0)) * 180.0 / np.pi

                        return angle

                    angle = calculate_angle(vector1, vector2)

                    # Determine color based on angle range
                    if 25 <= angle <= 125:
                        color = (0, 255, 0)  # Green
                    else:
                        color = (0, 0, 255)  # Red

                    # Draw lines and angle on the frame
                    shoulder_coord = tuple(np.multiply(shoulder, [640, 480]).astype(int))
                    elbow_coord = tuple(np.multiply(elbow, [640, 480]).astype(int))
                    torso_coord = tuple(np.multiply(torso, [640, 480]).astype(int))

                    cv2.line(image, torso_coord, shoulder_coord, color, 2)
                    cv2.line(image, shoulder_coord, elbow_coord, color, 2)
                    cv2.putText(image, f'{int(angle)}', shoulder_coord, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2,
                                cv2.LINE_AA)

                    # Draw the pose landmarks
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                except Exception as e:
                    print(f"Error during pose processing: {e}")

                # Encode the frame as JPEG and yield it
                ret, buffer = cv2.imencode('.jpg', image)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()
    print("Camera released")  # Debugging: Check if the camera is released


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    if request.method == 'POST':
        if 'login_submit' in request.form and login_form.validate_on_submit():
            user = User.query.filter_by(username=login_form.username.data).first()
            if user and user.check_password(login_form.password.data):
                flash('Login successful!', 'success')
                session['user_id'] = user.id
                return redirect(url_for('mainboard'))
            else:
                flash('Invalid username or password.', 'danger')
        elif 'register_submit' in request.form and registration_form.validate_on_submit():
            user = User.query.filter_by(username=registration_form.username.data).first()
            if user is None:
                new_user = User(username=registration_form.username.data, email=registration_form.email.data)
                new_user.set_password(registration_form.password.data)
                db.session.add(new_user)
                db.session.commit()
                user_exercise = UserExercise(user_id=new_user.id, exercise_id=None,
                                             count=0)
                db.session.add(user_exercise)

                weekly_workout = WeeklyWorkout(user_id=new_user.id, goal=5,
                                               completed=0)
                db.session.add(weekly_workout)
                db.session.commit()

                flash('Registration successful! You can now log in.', 'success')
                session['user_id'] = new_user.id
                session['first_session'] = True
                return redirect(url_for('mainboard'))
            else:
                flash('Username already exists. Please choose a different username.', 'danger')
    return render_template('enter.html', login_form=login_form, registration_form=registration_form)


@app.route('/mainboard', methods=['GET', 'POST'])
def mainboard():
    first_session = session.get('first_session')
    if not first_session:
        print('not first time')
    else:
        print(first_session)
        session['first_session'] = False
    search_form = SearchForm()
    user_id = session.get('user_id')
    if not user_id:
        print('error no id')
    weekly_workout = WeeklyWorkout.query.filter_by(user_id=user_id).first()

    if weekly_workout:
        print('success fetching id')
        workouts_completed = weekly_workout.completed
        weekly_goal = weekly_workout.goal
        workouts_remaining = max(weekly_goal - workouts_completed, 0)
        efficiency = (workouts_completed / weekly_goal) * 100 if weekly_goal > 0 else 0
        progress = (workouts_completed / weekly_goal) * 100 if weekly_goal > 0 else 0
    else:

        workouts_completed = 0
        weekly_goal = 3
        workouts_remaining = 3
        efficiency = 0
        progress = 0

    return render_template('mainboard.html', search_form=search_form,workouts_completed=workouts_completed,
                           weekly_goal=weekly_goal, workouts_remaining=workouts_remaining, efficiency=efficiency,progress=progress,
                           first_session=first_session)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    search_form = SearchForm()
    user_id = session.get('user_id')
    weekly_workout = WeeklyWorkout.query.filter_by(user_id=user_id).first()
    user_details = User.query.filter_by(id=user_id).first()
    if weekly_workout:
        print('success fetching id')
        weekly_goal = weekly_workout.goal

    if user_details:
        print('success fetching user details')
        username = user_details.username

    return render_template('profile.html', search_form=search_form, weekly_goal=weekly_goal,
                           username = username)


@app.route('/search_exercises', methods=['GET'])
def search_exercises():
    query = request.args.get('query', '').strip()
    if query:
        exercises = Exercises.query.filter(Exercises.name.ilike(f'%{query}%')).all()
        results = [{'name': exercise.name, 'link': exercise.link} for exercise in exercises]
        return jsonify(results)
    return jsonify([])

@app.route('/exercises', methods=['GET','POST'])
def exercises():
    search_form = SearchForm()
    return render_template('exercises.html', search_form=search_form)


@app.route('/leaderboard', methods=['GET','POST'])
def leaderboard():
    search_form = SearchForm()
    return render_template('leaderboard.html', search_form=search_form)



@app.route('/start')
def start():
    search_form = SearchForm()

    return render_template('start.html', search_form=search_form)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True)
