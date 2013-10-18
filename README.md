Automation folder information


----------------
Folder structure
----------------

/automation/tests_cases/ -- actual test cases captured here 
/automation/framework --  framework services and dao here
/automation/env_config -- enviroment configuration values
/automation/lib -- third party libraries 


-----
SETUP 
----

PYTHON               
•	Install python 2.6 - http://www.python.org/download/releases/2.6/
WIN SYSTEM variables
•	SYSTEM variable - PATHS
o	Path - Set path to add the following(python,python-scripts) - \;C:\Python26;C:\Python26\Scripts
Note: set these in System variables NOT user variables
Easy INSTALL 
•	Install setup tools - http://stackoverflow.com/questions/309412/how-to-setup-setuptools-for-python-2-6-on-windows
o	http://peak.telecommunity.com/dist/ez_setup.py
o	python.exe setup.py bdist_wininst

-- nose (unit test framework)
easy_install nose

--test-config (nose plugin, provides a faculty for passing test-specific (or test-run specific) configuration data to the tests)
easy_install nose-testconfig

-- requests (Requests allow you to send HTTP/1.1 requests)
easy_install requests

-------------
SETUP - linux
-------------

Download and build Python 2.6
•	sudo apt-get install python
or  Go to http://www.python.org/.

•	sudo apt-get install python-setuptools
or  http://pypi.python.org/pypi/setuptools

-- nose (unit test framework)
sudo easy_install nose

--test-config (nose plugin, provides a faculty for passing test-specific (or test-run specific) configuration data to the tests)
sudo easy_install nose-testconfig

-- requests (Requests allow you to send HTTP/1.1 requests)
sudo easy_install requests

-------
eclipse
-------
Users can use any IDE they wish, i have used eclipse, here are the main steps
and the some tips for configuration



Install the Eclipse Platform
sudo apt-get install eclipse-platform
or on windows now the eclipse executable


And launch it by typing "eclipse" in the command terminal. 
To install PyDev via the Eclipse UI
•	Click Help | Install new software.
•	Click Available Software Sites
•	Click Add.
•	Enter PyDev for the name.
•	Enter http://pydev.org/updates for the location. Click OK.
•	Click OK.
•	Select PyDev from the Work with drop down list.
•	Check PyDev in the list. Click Next. Click Next again. Accept the terms and click Finish.
•	Check the checkbox to trust the certificates and click OK. Restart Eclipse
NOTE: Eclipse Marketplace is available in 3.6 and can be accessed directly from the Eclipse platform(Under the help menu).
You can also access the Eclipse Marketplace by following this link: http://marketplace.eclipse.org/
 
Configure PyDev
•	Windows | Preferences | Pydev | Interpreter - Python
•	Click Auto Config.

 
Override Python Unit-test to use Nose
Windows | Preferences | Pydev | Pyunit
and select Nose Test Runner in the dropdown. The verbosity value is set to 0 by default. Change this to 2.
In the Test Runner dropdown, select Nose Test Runner
Click Apply and Ok 
