## Apache Redirect Rules Generator

This project is a Python script for generating Apache rewrite/redirect rules from a CSV of URL's.

## Compatible Platforms

The script has been tested on Mac OS X and Ubuntu 20.04 and should work ok on those platforms

## Limitations

**It is nowhere near ready for use in a production/working environment yet and should only be considered a proof-of-concept only at this point!**

The script will currently overwrite any file specified as the destination for the redirect/rewrite rules with its own contents every time the script is run so **any previous contents in that file will be lost and overwritten.**

At present, the redirects generated will rewrite the whole path of the source URL to a destination URL. Nothing more complex is supported at present. Nginx redirects/rewrites are not supported by this tool


## What It Can Do

The script will generate either [RedirectMatch](https://httpd.apache.org/docs/2.4/mod/mod_alias.html#page-header) lines or [Rewrite](https://httpd.apache.org/docs/2.4/mod/mod_rewrite.html) Rules for a given list of redirects supplied in a CSV file. It can automatically escape URL-encoded characters (e.g %20) in source URL paths to be redirected and produce rewrite rules for URL's that have a query string in them ,with either one parameter or multiple parameters 

Filename extensions in URL's are also accounted for in some small way.

For source URL paths that include a trailing slash, a rule will be generated that matches on both the version with a trailing slash and a version without one. For example, a source URL with the value `https://www.example.com/peter/` would generate a rule that matches on the path `/peter/` or `/peter`


Redirects with different [HTTP response codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#3xx_redirection) are catered for (currently only 301, 302 and 307 HTTP response codes are supported for generated redirects) and each individual redirect can have a different response code configured for it.


## Getting Data Into It and How it is Processed

The CSV file itself should have the following 3 field headings at the top of the CSV file:
 
-  **source**
-  **destination**
-  **redirect_code**

Description of each field required and how it is processed can be found below:

-  **source**: the source url for the redirect (only path, query strings and fragments are preserved). So that, for example, `https://www.example.com/peter` becomes `/peter`)

-  **destination**: the destination url for the redirect (full url is preserved)

-  **redirect_code**: the response code for the redirect (e.g, 301, 302)

  

## Information about the repository

There are 2 additional sub-directories in the repository apart from the **scripts** sub-directory where the script itself resides. Their purpose is described below:

-  **redirects**: This sub-directory can be used for storing the redirects/rewrite rules the script outputs. At present, any file named **.htaccess** or with a **.txt** extension is not tracked in the repository

-  **urls**: This sub-directory can be used for storing the csv files containing the redirects you want to generate and/or test. At present, any file with a **.csv** or **.bak** extension is not tracked in the repository. There is an example CSV file in this directory called **urls.csv.example** that you can use as test input data for the script.


## Getting started: Installation

You'll need Python 3 on your local system to use it. Its best to run it in a python virtual environment using the instructions below. You'll need the **venv** python module installed on your local system to do this.

More information on using virtual environments with Python can be found [here](https://docs.python.org/3/tutorial/venv.html)

If you are running this on Ubuntu, you may need to install the `python3-venv`, `python3-dev` and `build-essential` packages using the command `sudo apt install python3-venv python3-dev build-essential` before starting with the steps below. These steps assume you are running this on Ubuntu/Mac OS X but [WSL](https://docs.microsoft.com/en-us/windows/wsl) running on Windows should work ok as well.
  
- Checkout/clone the git repository to a directory on your local machine
- cd into the **scripts** sub-directory of the repository
- Give the script execute permissions with the command: `chmod +x redirectgen.py`
- On your local system, run the command: `python3 -m venv env`
- On your local system, run the command: `source env/bin/activate`
- run the command: `pip install -r requirements.txt` to install the dependencies to the virtual environment

## Usage

For more information, see the examples further down.
```
usage: redirectgen.py [-h] -u URLS -o OUTFILE

optional arguments:
  -h, --help            show this help message and exit
  -u URLS, --urls URLS  path to csv file containting the redirect urls we want to process
  -o OUTFILE, --outfile OUTFILE
                        path for the file we want to output the finished redirects to
 ```


## Example: Using the Script (Just Generating Redirects Using Example Data)

Example of how to do this is below:

 - cd into the top-level directory of the repository
 - Copy the file **urls.csv.example** in the **urls** sub-directory to **urls.csv**
 - Setup the script and Python Virtual Environment using the instructions above.
 - Run the command: `./scripts/redirectgen.py -u urls/urls.csv -o redirects/.htaccess`on your local machine

The example above will take in URLs from a CSV file located at `urls/urls.csv` and output redirects/rewrite rules to the file located at `redirects/.htaccess`

Using the **urls.example.csv** in the repository will generate the redirects below in the redirects output file:

    RedirectMatch 301 ^/peter\x20lavelle\.pdf\.exe$ https://www.google.com
    RedirectMatch 302 ^/peter\x20lavelle\.pdf\.exe\.doc$ https://www.google.com
    RedirectMatch 301 ^/peter\x20lavelle\.pdf\.exe\.doc2$ https://www.google.com
    <IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_URI} ^/peterlavelle\.jpg$
    RewriteCond %{QUERY_STRING} ^myquery$
    RewriteRule ^(.*)$ https://www.yahoo.com/thisisatest [R=301,L,QSD]
    </IfModule>
    <IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_URI} ^/peter\x20lavelle\.jpg$
    RewriteCond %{QUERY_STRING} ^myquery$
    RewriteRule ^(.*)$ https://www.yahoo.com/thisisatest [R=302,L,QSD]
    </IfModule>


**Note that, at present, the script will overwrite the redirects file each time it is run, so any contents in the redirects file will be lost and replaced with the newly-generated redirects/rewrites.** 

  

## Example: Using the Script (Generating and Testing Redirects with Lando Using Example Data)

There is a **.lando.yml** file in the repository that you can use to bring up an Apache container to serve as a local instance to test the redirects generated by the script. You will need Lando installed on your local machine to make use of this.

You can copy the **urls.csv.example** file in the **urls** sub-directory to **urls.csv** to follow along with this example:

If you are new to Lando, more information on getting started with installing it can be found [here](https://docs.lando.dev/basics/installation.html)

To use the Lando instance to test your redirects, follow the steps below:

- cd into the top-level directory of the repository on your local machine
- Start the Python Virtual Environment on your local system for the script using the instructions above.
- run the command `lando start`to bring up the lando instance. 
- When lando has finished setting everything up you should get something similar to this in your terminal:  

		 NAME            redirectstester                
		 LOCATION        /home/user/redirects-generator 
		 SERVICES        webserver                      
		 WEBSERVER URLS  http://localhost:49154         
					      http://redirects.lndo.site/
	
	The **.lando.yml** file is configured to bring up the Apache container with the URL: http://redirects.lndo.site
	We will need this URL for the next step.

- The lando instance is configured to use the **redirects** sub-directory of the repository as its Document Root. We will take account of this in the example command in the next step. 

 - Run the following command from the top level directory of the repository on your local machine to generate a set of redirects/rewrites and output them to a .htaccess file so they can be picked up by the Lando Docker container:  `./scripts/redirectgen.py -u urls/urls.csv -o redirects/.htaccess`

 - On Mac OS X or Linux Use the command `curl -I -L  http://redirects.lndo.site/your/redirect/source/path` to test your redirects. Replace `/your/redirect/source/path` with the source path of the particular redirect you are testing. More information on the curl utility can be found [here](https://curl.se/docs/manpage.html)
