# ZEPHYR SQUAD REST API

It's an project to use some ZEPHYR SQUAD REST APIs to create cycle, folders and add tests as well update status of them</br>

# How to install

First of all, you have to clone this project.</br>

```
git clone https://github.com/araujosnathan/zephyr-squad-rest-api.git
```

Enter in `zephyr-squad-rest-api` folder and install dependecies

```
pip install -r requirements.txt
```

Check the `zephyr_config.json` to put the config values that you need to your project<br>

# Notes

You can use the `environment variables` to put your credentials, if these values were not in config file, it will get from environment variables.<br>
If you put the credentials in config file, it will use them even you have set any environment variable

# Command to populate cycle and folders with tests

```
python zephyr_squad.py --command populate --config_file zephyr_config.json --version_name <version_name>
```

# Command to publish test result to automated folder

Note: For the moment, we are filtering by @ER-XXXX key regex in Mochawesome file to find the tests to be updated.<br>
If your key is different in Jira, try to change the `PATTERN` in `support/utils.py`
We are trying to find this pattern in test result file: `@YOUR_JIRA_KEY` in the title of the test

```
python zephyr_squad.py --command publish --config_file zephyr_config.json --version_name <version_name> --test_result_file <mochawesome_report>
```
