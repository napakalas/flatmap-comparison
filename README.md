# flatmap-comparison

Comparing flatmaps generated using different SCKAN versions (i.e. production and staging)

Instruction

1. Clone this repository
2. Go to the repository's directory
3. Installation
   ```
    ./install.sh
   ```
   This command executes a script to:
   * clone and install mapmaker using poetry
   * install other packages for this application using poetry
   If you dont want to install mapmaker, just `poetry install` from the main directory.
4. Compare using shell script
   * syntax
     ```
     ./compare_map.sh [<species>] [json|csv|xlsx] [*opt refresh]
     ```
     species = pig | cat | mouse | rat | female | male | functional-connectivity
   * example
     ```
     ./compare_map.sh cat json
     ```
       * for this example, if a cat-flatmap comparison has never been done, it will be cloned from the repository, generated flatmaps for staging and production, compared, then the results are stored in `results/cat.log`
       * if the comparison has already been done, then no cloning is done, and generates flatmaps.
     ```
     ./compare_map.sh cat json refresh
     ```
       * do the comparison as `./compare_map.sh cat json` as if you've never done a comparison.
   * The comparison results are stored in `results` directory as `cat.log`.
5. Compare using python (via poetry)
   * syntax
     ```
     poetry run python fcompare.py \
        --production <production> \
        --plog <production-log> \
        --staging <staging> \
        --slog <staging-log>
     ```

     * --production : path to flatmap with production SCKAN
     * --plog       : path to flatmap log with production SCKAN
     * --staging'   : path to flatmap with staging SCKAN
     * --slog'      : path to flatmap log with staging SCKAN'
     * --output'    : a file path and name to store comparison results (xlsx, json, csv)
   * example

     ```
        poetry run python fcompare.py \
        --production ../production/human-flatmap_male \
        --plog ../flatmaps/production/male.log \
        --staging ../flatmaps/staging/human-flatmap_male \
        --slog ../flatmaps/staging/male.log --output ../resuls/male.csv
     ```
