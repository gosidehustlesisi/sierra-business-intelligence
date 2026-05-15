# Netflix Titles Dataset — Data Dictionary

**Source:** [Kaggle — Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)  
**Author:** Shivam Bansal  
**Records:** 8,807 titles  
**Last Updated:** 2021 (Kaggle version 5)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `show_id` | string | Unique identifier for each title | `s1`, `s2` |
| `type` | categorical | Content format — Movie or TV Show | `Movie`, `TV Show` |
| `title` | string | Title of the content | `Dick Johnson Is Dead` |
| `director` | string | Director(s), comma-separated for multiple | `Kirsten Johnson` |
| `cast` | string | Main cast, comma-separated | `Chadwick Boseman, Viola Davis` |
| `country` | string | Production country(ies), comma-separated | `United States` |
| `date_added` | date | Date the title was added to Netflix (UTC) | `September 25, 2021` |
| `release_year` | integer | Original theatrical or broadcast release year | `2020` |
| `rating` | categorical | Content rating (TV-Y, TV-G, PG, TV-14, R, etc.) | `PG-13` |
| `duration` | string | Runtime in minutes (Movies) or seasons (TV Shows) | `90 min` / `2 Seasons` |
| `listed_in` | string | Genres/categories, comma-separated | `Documentaries` |
| `description` | string | Plot summary / synopsis | `As her father nears the end...` |

## Data Quality Notes

- **Missing values:** `director` (~30%), `cast` (~9%), `country` (~6%), `date_added` (~0.1%)
- **Multi-value fields:** `country`, `cast`, `director`, `listed_in` contain comma-separated entries requiring normalization for analysis
- **Temporal coverage:** `release_year` spans 1925–2021; `date_added` spans 2008–2021
- **Country field:** Titles may list multiple production countries; primary country is typically the first listed

## Usage

Load with pandas:

```python
import pandas as pd
df = pd.read_csv("data/netflix_titles.csv")
```
