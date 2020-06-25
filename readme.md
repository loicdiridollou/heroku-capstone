The app is running on Heroku at: https://ld-udacity.herokuapp.com/
The different endpoints have been implemented. I have mostly reused previous projects code to build this new app, and of course modifying the parts to have it correspond to all the expectations of this project.
To test the code, launch the Postman json collection, the Bearer Token are already set in the collection.
As the database is not densely populated, it is crucial to run the test in order to avoid an unpopulated database if the Delete tests were run too often, drying up the tables.

The Python unittest does not support the bearer token authentification thus it was impossible to run the test in Python directly (I haven't found the way to).