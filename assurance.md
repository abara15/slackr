# Assurance - ThunderHands


In order to provide assurances that our backend implementation is fit for purpose, we first had to write user stories prior to development. When developing our user stories, we followed the INVEST strategy:
        
* __Independent:__ User stories shouldn’t need to rely on each other.
* __Negotiable:__ User stories should avoid too much detail
* __Valuable:__ The user story is of value to the client
* __Estimable:__ Story is clear enough to estimate needed time.
* __Small:__ Each user story should be small, and deliverable within time.
* __Testable:__ Clear acceptance criteria.

These user stories were largely based on the functions outlined to our team in the project specifications, as well as based on our own assumptions which were compiled in Iteration One.

Our team broke down these user stories into acceptance criteria that must be met for the client. This was written in a more natural tone, with minimal technical detail so it would appear more understandable to the client. Despite these being written prior to development, they were further refined by the team during the development stage of the project.

Verification determines if the system has been built right. Validation establishes if the right system has been built. In order to verify this program, we developed a wide range of tests. We did this by creating tests that tested data which is supposed to bring up either a ValueError or AccessError – for example, name_first being greater than 50 characters in the user_profile_setname function. Additionally, tests were also created that tested valid data to ensure that the system is working and processing the data correctly. As a result, we thus checked our code coverage to ensure that our tests will test all lines of code for each function.

Since each team member was assigned certain functions to write, there was an inconsistency in the style and structure of the code. As a result, once all the functions were complete, we used Pylint in order to detect any errors and potential errors in the complete code, and to check the code against Python conventions. This allowed us to thus refine the code so it would appear neater and consistent, which is easier for the team to maintain. Also, allowing for a uniform code that was simpler to understand for each member, as the variation between code was reduced.
