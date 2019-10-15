Database_url: postgres://wpgbvssvitxlbo:8b9b80b9e1bc3a0f02d08709132aea152fbb8669dfe630e519716da5cc41a346@ec2-79-125-4-72.eu-west-1.compute.amazonaws.com:5432/d1jcss8rl8tocd

A video of my website can be found above too.

# Documentation:

This website uses flask alongside html and css.

The user is always requried to sign in before accessing any pages which is enforced in my application.py where i'll direct them to the signup page if they have not logged in/registered.

Regarding credentials of the users, usernames have to be unique (a check on the database on whether the username exists will be performed). And all usernames, passwords, and emails cannot be null.

In the forum, users will be able to view other people's blogs, they have the freedom to either type tags of the relevant animal they wish to search up or type a substring of a title of a blog they want to find. They can also choose to display the blogs in order of time and rating.

There is also a page in the navbar which allows the user to only view his/her blogs.

The "create new blog" page, takes in 3 input. (Title, content, animal). And a new blog will be appended to the database via the sql command.

There is also a personal profile page where users are able to view their username, email and number of blogs which they posted.

When the "click to view more details" button is clicked, the user is redirected to a page dedicated to that blog. (made through the dynamic url function in flask for e.g. <string:blogid>), where the content of the blog will be displayed.

Lastly, there is a logout button at the top right hand corner of the screen where upon clicking, the username, password and email will be popped from the session, and the user will be brought to the login page.
