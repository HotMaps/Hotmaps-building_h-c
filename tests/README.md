* in this directory, run `pytest`
* create new test modules in modules/ directory
* functions which should be run by pytest must start with *test*
* put the root-url of your api into *test_settings.py* (copy from test_settings_example.py) (ie. port!)
* to simply have request responses compared against predifined json files, use gen_tests() from test_common.py (see example module)
