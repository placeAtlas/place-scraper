# `place-scraper`

This is a repository that hosts the scraper of the r/place canvas, utilized for The 2023 r/place Atlas.

This is based upon https://github.com/ProstoSanja/place-2022, adapted to output images to be used on the Atlas.

The scraper results are uploaded on https://archive.org/details/place-atlas-2023-scraped-canvas. Keep in mind that the script is continuously adjusted until `images5`, which is the state of the code that is uploaded in this repository.

## Usage

1. Install Python (recommended: 3.10) and all the required dependencies.

   ```sh
   pip install -r scraper/requirements.txt
   ```

2. Edit `authparams.py` with your Reddit accounts credentials and the application credentials of the type `script`.

   ```python
   USERNAME=""      # Account username
   PASSWORD=""      # Account password
   OAUTH_CLIENT=""  # Application client ID (below "personal  use script")
   OAUTH_SECRET=""  # Application secret
   AUTH_TOKEN=""    # For manual overrides, may be left empty
   ```

3. If needed, configure fetch interval inside the script.

4. Run `scraper/scraper.py`

   ```
   python scraper/scraper.py
   ```
