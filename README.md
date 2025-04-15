# panelcreator
A class for creating panels of images with annotations.

## Example Usage

```python
from panelcreator import PanelCreator, TextBox, ObjectDatabase
## Read the data ##
df = pd.read_csv('img_VIed_archived.csv')
db = ObjectDatabase("image_cut.npy")

df_sample = df.loc[[5, 7, 9, 11]]

pc = PanelCreator(df_sample, 1, 4, db)
format_string = "Object ID ${id}$"
boxlist = [
    TextBox(0.02, 0.98, "Metric A: ${metric_a:.1f}\\pm{metric_a_err:.1f}$", size=9, c='white', va='top'),
    TextBox(0.02, 0.88, "Metric B: ${{{metric_b:.2f}}}^{{+{metric_b_hi:.2f}}}_{{-{metric_b_lo:.2f}}}$", size=9, c='white', va='top'),
    TextBox(0.97, 0.02, "Tags: {tag1}, {tag2}", size=9, c='white', va='bottom', ha='right'),
    TextBox(0.5, 0.5, "SAMPLE", size=25, c='white', va='center', ha='center', alpha=0.5, rotation=45)
]
pc.create(figsize=(8, 3), title_format=format_string, title_size=9, mark=False, textboxs=boxlist)
pc.title("Demonstration of the PanelCreator", title_size=16)
plt.show()
```

You can also use
```python
pc.save_all(path)
```
to save all the panels to a specified path.
