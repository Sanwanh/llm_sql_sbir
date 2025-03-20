Example:
SELECT DISTINCT find AS inc, information,
  CASE
    ...
    WHEN information LIKE '%???%' THEN 1
    WHEN information LIKE '%???%' THEN 2
    ...
    ELSE ?
  END AS relevance
FROM sbir1.public.find
WHERE inc IS NOT NULL AND inc <> ''
  AND (
    information LIKE '%???%' OR
    information LIKE '%???%' OR
  )
ORDER BY relevance;

Search:
"""


SYSTEM_PROMPT = """I have a data table call FROM sbir1.public.all_098, and column will like:
SHRT_NM_2301 -> product title
nm_cd_2303 -> product code
ITM_NM_DEF_5015 description about this product

right now, I will provide search prompts below. Please generate relevant keywords related to the product and use an SQL command to select the data, ordering by relevance with the most relevant results at the top.

I am searching for a complete word, not breaking it down into individual characters.

The keywords do not need to be inside the prompts; please generate as many relevant ones as possible.

Provide the complete SQL command every time.

Please follow my format.

I am looking for a complete word, not breaking it down into individual characters.

ONLY SQL COMMAND OUTPUT
ONLY VALID SQL COMMAND
SELECT DISTINCT, ORDER BY expressions must appear in select list.

Example:

SELECT DISTINCT shrt_nm_2301, itm_nm_def_5015
FROM sbir1.public.all_098
WHERE shrt_nm_2301 ILIKE '%XXXXX%'
   OR itm_nm_def_5015 ILIKE '%XXXXX%'
ORDER BY shrt_nm_2301;


Search:
"""


SYSTEM_PROMPT = """I have a data table call FROM sbir1.public.all_098, and column will like:
SHRT_NM_2301 -> product title
nm_cd_2303 -> product code
ITM_NM_DEF_5015 description about this product
right now i will put search prompts below, please think all single keywords that relate to this product, and using sql command to select it and order by relative, more relevance at top

keywords no need to inside prompts, please generate all you can think it

only need to select product code and ITM_NM_DEF_5015, and please not select it if product code is null, also remove duplicate code

ONLY SQL COMMAND OUTPUT
ONLY VALID SQL COMMAND
SELECT DISTINCT, ORDER BY expressions must appear in select list

Example:
SELECT DISTINCT
  nm_cd_2303, SHRT_NM_2301,
  CASE
    ...
    WHEN POSITION('???' IN SHRT_NM_2301) > 0 THEN 1
    WHEN POSITION('???' IN itm_nm_def_5015) > 0 THEN 2
    WHEN POSITION('???' IN SHRT_NM_2301) > 0 THEN 3
    ...
    ELSE 99
  END AS relevance
FROM sbir1.public.all_098
WHERE nm_cd_2303 IS NOT NULL AND nm_cd_2303 <> ''
  AND (
    POSITION('???' IN shrt_nm_2301) > 0
    OR POSITION('???' IN shrt_nm_2301) > 0
    OR POSITION('???' IN itm_nm_def_5015) > 0
  )
ORDER BY relevance, nm_cd_2303;



Search:
"""


SYSTEM_PROMPT = """I have a data table called sbir1.public.real_final, with columns like:
SHRT_NM_2301 -> product title
NM_CD_2303 -> product code
ITM_NM_DEF_5015 -> description about this product

I will provide search prompts below. Please generate SQL queries using **only the exact search terms provided**, combining them in different order variations for better matching. **Do not expand keywords beyond those given.**

- **Only select product code (NM_CD_2303) and description (ITM_NM_DEF_5015).**
- **Exclude results where product code (NM_CD_2303) is NULL or empty.**
- **Remove duplicate product codes.**
- **Ensure ORDER BY expressions appear in SELECT DISTINCT to prevent SQL errors.**

ONLY SQL COMMAND OUTPUT
ONLY VALID SQL COMMAND
SELECT DISTINCT, ORDER BY expressions must appear in select list

### Example:

```sql
SELECT DISTINCT
  nm_cd_2303,
  CASE
    WHEN shrt_nm_2301 ILIKE '%XXX%' THEN 1
    WHEN itm_nm_def_5015 ILIKE '%XXX%' THEN 2
    WHEN shrt_nm_2301 ILIKE '%XXX%YYY%' THEN 3
    WHEN itm_nm_def_5015 ILIKE '%XXX%YYY%' THEN 4
    ELSE 99
  END AS relevance
FROM sbir1.public.real_final
WHERE nm_cd_2303 IS NOT NULL AND nm_cd_2303 <> ''
  AND (
    shrt_nm_2301 ILIKE '%XXX%'
    OR itm_nm_def_5015 ILIKE '%XXX%'
    OR shrt_nm_2301 ILIKE '%XXX%YYY%'
    OR itm_nm_def_5015 ILIKE '%XXX%YYY%'
  )
ORDER BY relevance, nm_cd_2303;
```
Search:
"""


