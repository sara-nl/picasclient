PiCaS token commands
============

This page introduces the most used commands for preparing and editing tokens. 

### Connect to token pool server on CouchDB

To approach the DB, you have to fill in the `examples/picasconfig.py` with the information to log in to your CouchDB instance and the database you want use for storing the work tokens. Specifically, the information needed are:
```
PICAS_HOST_URL="https://picas.surfsara.nl:6984"
PICAS_DATABASE=""
PICAS_USERNAME=""
PICAS_PASSWORD=""
```
### Create views
Once you can approach the server, you have to define "view" logic, so that you can easily view large numbers of tokens and filter on new, running and finished tokens. To create these views, run:

```
python createViews.py
```

### Create tokens
This example includes a bash script `(./createTokens)` that generates a sensible parameter file, with each line representing a set of parameters that the fractals program can be called with. Without arguments it creates a fairly sensible set of 24 lines of parameters. You can generate different sets of parameters by calling the program with a combination of `-q`, `-d` and `-m` arguments, but at the moment no documentation exists on these. We recommend not to use them for the moment.
```
./createTokens
```
After you ran the `createTokens` script you’ll see output similar to the following:
```
/tmp/tmp.fZ33Kd8wXK
cat /tmp/tmp.fZ33Kd8wXK
```

### Upload tokens to the PiCaS server


Next you have to send some tokens containing work to the CouchDB instance. You can send two types of work in this example. For very fast running jobs, send the `quickExample.txt` file with:
```
python pushTokens.py quickExample.txt
```

For longer jobs example with a set of 24 lines of parameters. send the file generated in the create tokens step:
```
python pushTokens.py /tmp/tmp.fZ33Kd8wXK
```

### Reset tokens 

### Delete tokens

To delete all the Tokens in a certain view, you can use the `deteleTokens.py` under the `examples` directory. For example to delete all the tokens in todo view, run
```
python /path-to-script/deleteTokens.py Monitor/todo
```
