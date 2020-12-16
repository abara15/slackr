Refactor or add to your code from iteration 2 to utilise good software engineering design to make your code more maintainable. Use a range of principles discussed in lectures.

As you modify your code, maintain a up to a 2 page markdown file that lists the key changes you've made in your code and why they've been made. 

Write this in seprinciples.md.


# Refactors
Please note that the actual changes of our code are clearly defined in our descriptions for commits to the repository and can be seen there.

* Switched formatter to use black instead of autopep.
* Refactored code to follow style guide (variable naming, spacing, etc).
* Added expiry timestamp to generated JWT, not have any tokens that are valid forever.
* Refactored routes to use a default error handler and added correct error attributes for frontend to display errors (iteration 3).
* Refactored db.py to include constants as class attributes.
* Refactored routes to parse params in the same place instead of across multiple functions.
* Removed unnecessary function calls from tests and used helpers to reduce dulpicate code.
* Refactored code in search.py, so if the u_id not in channel or the query string is empty, it will return an empty list, otherwise it will search all messages in all channels for a message that relates to that query, and will append it to a list which is thus returned.
* Refactored code in users.py. I saw that there was repetition in the error raises in my setname and sethandle functions, so I turned the error check into the function len_error and just called this function from setname and sethandle.
* Refactored code in users.py. I saw that there was repetition in the error raises in my setname and sethandle functions, so I turned the error check into the function len_error_check and just called this function from setemail and sethandle.
* Refactored code in standup.py. I saw that there was repetition in the error raises over some of the functions, so I pulled these error raises into their own functions and called these error functions from my primary functions.
* As we each had done been assigned individual functions to work on, the code was not of a uniform style. To resolve this issue, we each looked at eachothers code and together we tidied it up so that it was uniform and consistent. 
* Additionally, we did this with tests for each functions as we each wrote the tests for the functions we had been assigned. This cleaned up the appearance of the tests and ensured consistentcy. 
* Refactored code in tests to ensure that tests for similar/same functions were written up in a similar way for easy understanding and readability. Ensured code for the tests were simple and straight forward, removing any unnecessary repetition or confusion.
