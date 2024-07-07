# Based on user survey data, post cleaning and standardizing, we have the following information on exercises:
![download](https://github.com/ohksith/Workout-Form-Checker/assets/79146902/ac441d45-ca55-4011-8a79-e02e32b0d206)
```
plt.style.use('seaborn-v0_8-notebook')
plt.title('Exercises that users find difficult / Risky')
ex_graph = ex['Exercises'].value_counts().plot(kind='barh')
```

# Based on exercise data, these are the bodyparts mentioned the most
![download](https://github.com/ohksith/Workout-Form-Checker/assets/79146902/c4939316-85c7-49f5-a410-d33b40e45a77)

```
b_parts = {'Body Parts': ['Back','Chest','Shoulder','Triceps','Glutes','Hamstring','Trapezius','Biceps','Quads'], '%':[12,4,6,7,10,10,7,4,3]}
b_parts_graph = pd.DataFrame(b_parts)
pie = plt.pie(b_parts_graph['%'], labels=b_parts_graph['Body Parts'], autopct='%1.1f%%', colors=sns.color_palette('rocket', len(b_parts_graph)))
plt.title('% Distribution Across Body Parts')
```
