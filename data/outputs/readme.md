# Output

Available outputs are

- 0.25km, 1km and 4km resolutions solar insolation raster data
- 0.25km, 1km and 4km resolutions error raster data (RMPSE- Room Mean Percentage Square Error)

To get output at different resolutions add resolution to res dictionary in the app.py file with key as resolution in degree and value as string in km.
current resolutions are:

```python
res = {0.03455: '4km',
       0.0086375: '1km',
       0.002159375: '0.25km'
       }
```
