# Teamwork - ThunderHands

## Iteration 2:

* We only had two physical meetings, at night after our lab sessions on Monday. This was because it was the only time we were able to get everyone together for a physical meeting.
* Since we only had a small amount of meeting we made sure that they were useful and successful. So during the labs we'd all spend some time discussing what still had to be done for the project and have a short standup. We'd also spend some time working on the parts that needed us to be on the same page
* The majority of our communication was done online, via Facebook Messenger, and this was a very useful tool because team members were often quick to reply.
* Methods for how meetings were successful - started the meetings with discussing where everybody was at and if they didn't understand a specific part of the specifications to raise their concerns now so another team member could answer their questions. We then discussed what else needed to be done and by whom, and at the end of the meeting, we set a deadline during the week to aim to have our work done by.
* When things didn't go to plan, we redistributed our work between team members. For example, Anthony was having some trouble writing the standup functions, so Omar helped fix what he had already written in the functions, and Anthony went to make a start and draft the markdown files.
* During this iteration, we largely followed the same strategies of splitting up work as we did in the previous iteration. In the previous iteration, each person wrote autotests for eight functions each. In this iteration, the same team member wrote the functions that correlate with the same tests they wrote. Each team member wrote their functions on their branch in a file separate to their flask routes, and then this was all pushed to master and combined the flask routes were edited to call the functions. After this was all done, the team went through the code and edited it in order to try and maintain a consistent flow and style of code.
* Since it can be hard to communicate over text for some problems our group would sometimes call to solve some problems that we we're having. This allowed us to be able to talk while not having to physically meet up.
* As a team we tried to finish most of the backend implementation a little early so that we could have more time to iron out any problems and also know what the hardest part of the project would be
* During the project there were some changes to the spec and our understanding of the project as we learnt more from lectures and discussions and so we had to change our implementation a bit rather than just following the plan from iteration one.
* During the project there were some changes to the spec and our understanding of the project as we learnt more from lectures and discussions and so we had to change our implementation a bit rather than just following the plan from iteration one.
* Communication online is extremely good. If someone is stuck and sends a message asking for suggestions on what to do, or doesn't understand how something works, they will get a response on the topic and an explanation.



## Iteration 3:

* Our group had a meeting every week after each tutorial/lab. It was difficult for us to meet more often than this, as we all live very far apart, and our timetables often clashed, so this was the only time we were all free on campus.
* These meetings would be of varying timespans, some were brief if we just had to confirm a couple things while others were longer when there were bigger issues. 
* Most of our communication was done online via Facebook Messenger. We found this to be a very easy means of communication for our team, and we believed it worked well and was a major catalyst for our success in integrating our code with the front end.
* If someone ran into problems that they couldn't handle themselves, we would communicate online to fix these issues and solve the problem.
* Before beginning to write any new code, each member would message the other members to let them know what they were working on, and would then notify the rest of the group once they made changes to the code to pull new changes from the repository. This ensured we avoided multiple group members working on the same code at the same time, and prevented people from causing unneeded errors and raising new issues.
* In order to ensure that our meetings were successful, we developed a checklist of different things to discuss during our meetings.
    * We would have everybody say what they have done over the past week, and what they had to still do over the following week.
    * We set deadlines for different tasks and examined the workloads of each team member to ensure everybody could handle their individual workloads in conjunction with their other courses.
    * Anybody who had any questions or didn’t understand what to do raised their queries, which were further discussed by the rest of the team to ensure that everybody had a good understanding of what was going on.
* Not everything went to plan during this iteration.
    * For example, we had some issues with integrating our code to the front end, where Luke and Anthony found that we kept receiving the error message, “The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application”, when users tried sending messages on the channel, which would just appear blank.
    * In the end, Omar figured out that this occurred because a key error was thrown since in our code, the "img_url" on the user object is sometimes written as "image_url" and was able to push a fix for this.
* There wasn’t much crossover where multiple people worked on the same functions during this iteration. This is because we were generally just fixing up the functions that we each worked on in the previous iteration if that function was the cause for an error that appeared on the front end.
    * The only function we had left to write was the "upload_photo" function. This was assigned to Anthony, who has been working on the bulk of the user functions since iteration 2 but was also worked on by other members of the team due to its difficulty.
    * For this function, we just had Anthony write it up on his branch and then push it to the master branch. This function brought up some errors on the front end and was then worked on by both Anthony and Omar on the master branch.
    * The only other incident our team had with multiple people working on the same code was that Luke and Liam were both working on fixing up the tests for "message_sendlater".
* We believe that we worked well collaboratively on the same code, because we were constantly updating the rest of the team on our Messenger group when we made changes to code, and informed everyone to pull the latest code from the repository.

* Our team did a very good job on covering tests, members reviewed other peoples tests to ensure that they worked well and covered issues. This led us to having many tests that work to see any slips in our code.
