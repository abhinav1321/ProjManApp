# ProjManApp

PjojManApp is a Project Management App which works like Trello.com

## Features Included
  1. Registration of a new user and creating his account. 
      Accounts can be either free or premium
  
  2. The account have multiple boards.
  
  3. Boards consists of lists and lists consists of cards.
  
  4. Cards have a due date and attachments.
 
  5. Cards can be moved to any list of the current board.
  
  6.  Cards can be moved within the list. 
      (Implemented with a databse field named priority on card model,
        Which can be looped in correct order with a javascript function)
      
  ## A few more Features Added
  
  1. Users as board admin and board member.
          (Implemented by using the Models- Team and TeamMembers).       
The Model Team contains a foreignkey to Model Board, 
and Model TeamMember contains a foreignKey to Model Team

2. Adding Users on a Specific card
   --All the added users on a particular Board are Available to be added on any Card in the Board's umbrella .
   
   ..Implemented by using a Search Field for available users, and then adding the searched users.

## Screenshots

Index Page
![Index](https://github.com/abhinav1321/ProjManApp/blob/main/index.png)  
Index after log in
![index ](https://github.com/abhinav1321/ProjManApp/blob/main/loggedinindex.png)

Sign Up
![Signup](https://github.com/abhinav1321/ProjManApp/blob/main/signup.png)

Boards
![Boards](https://github.com/abhinav1321/ProjManApp/blob/main/boards.png)


Lists
![Lists](https://github.com/abhinav1321/ProjManApp/blob/main/lists.png)

Cards
![Cards](https://github.com/abhinav1321/ProjManApp/blob/main/cards.png) 

![card](https://github.com/abhinav1321/ProjManApp/blob/main/card_change.png)



Edit Card
![Edit card](https://github.com/abhinav1321/ProjManApp/blob/main/card_change.png)


Adding Users to Card
![Add user to card](https://github.com/abhinav1321/ProjManApp/blob/main/add_user_to_card.png)


File Upload
![file upload](https://github.com/abhinav1321/ProjManApp/blob/main/fileupload.png)


Change list 
![change](https://github.com/abhinav1321/ProjManApp/blob/main/chenge_user_to_list.png)



## Steps To Run
Clone The Project into your local system using below command

```
  git clone https://github.com/abhinav1321/ProjManApp

```
Open the project in terminal, Go to project folder and Run:

```
  pip3 install -r requirements.txt
```

Run the Django App

```
python manage.py runserver
```

Start Browsing

```
http://127.0.0.1:8000/
```
