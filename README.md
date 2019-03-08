# Flango
Flask based GUI for importing data into MongoDB

Flask based app for importing excel and csv ( semicolon or comma as delimiters) using pandas to Mongo database.
Nothing fancy

Flango could be nicely compiled to .exe  by [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) just needed to add xlrd as hidden import 

Note: [The MongoDB Query Language cannot always meaningfully express queries over documents whose field names contain these characters (see SERVER-30575). Until support is added in the query language, the use of $ and . in field names is not recommended and is not supported by the official MongoDB drivers.](https://docs.mongodb.com/manual/core/document/)
