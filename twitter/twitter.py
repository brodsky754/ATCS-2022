from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:
    """
    The menu to print once a user has logged in
    """
    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        while(True):
            user = input("What do you want your username to be?")
            password = input("Enter a password:")
            verify = input("Re-enter your password:")
            check_new = db_session.query(User).where(User.username == user).first()
            if(verify is not password or check_new is not None):
                print("That username is taken or your passwords don't match")
            else:
                break
        new_user = User(user, password)
        self.logged_in = True
        self.curr_user = new_user
        db_session.add(new_user)
        db_session.commit()
        print("Welcome " + user)

    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        while(True):
            user = input("Username:")
            password = input("Password:")
            person = db_session.query(User).where(User.password == password and User.username == user).first()
            if(person.username is not user or person.password is not password):
                print("Invalid username or password")
            else:
                break
        print("Welcome " + person.username)
        self.logged_in = True
        self.curr_user = person

    
    def logout(self):
        self.logged_in = False
        self.curr_user = None

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        print("Select a menu option:")
        option = input("1.Login\n2.Register User\n3.Exit")
        if(option == "1"):
            self.login()
        elif(option == "2"):
            self.register_user()
        elif(option == "3"):
            self.end()

    def follow(self):
        who = input("Who do you want to follow?")
        person = db_session().query(User).where(User.username == who).first()
        if(person == None):
            print("This person doesn't exist in our twitter database.")
            return
        elif(person in self.curr_user.following):
            print("You cannot follow someone that you already follow.")
            return
        self.curr_user.following.append(person)
        db_session.commit()
        print("You now following @" + who)

    def unfollow(self):
        who = input("Who do you want to unfollow?")
        person = db_session().query(User).where(User.username == who).first()
        if(person == None):
            print("This person doesn't exist")
            return
        elif(person not in self.curr_user.following):
            print("You don't follow this person")
            return
        self.curr_user.following.remove(person)
        db_session.commit()
        print("You have unfollowed @" + who)

    def tweet(self):
        tweet = input("New Tweet:")
        tags = input("Add tags seperated by spaces:")
        tag_list = tags.split()
        timestamp = datetime.now()
        new_tweet = Tweet(tweet, timestamp, self.curr_user.username)
        for tag in tag_list:
            new_tag = Tag(tag)
            new_tweet.tags.append(new_tag)
        db_session.add(new_tweet)
        db_session.commit()
        print(new_tweet)
    
    def view_my_tweets(self):
        result = db_session.query(Tweet).filter(self.curr_user.username == Tweet.username).all()
        for tweet in result:
            print(tweet)
            print("============================")
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        tweets = (
            db_session.query(Tweet)
            .join(Follower, Tweet.username == Follower.following_id)
            .filter(self.curr_user.username == Follower.follower_id)
            .order_by(Tweet.timestamp.desc())
            .limit(5)
        )
        for tweet in tweets:
            print(tweet)

    def search_by_user(self):
        username = input("Search for user:")
        user = db_session.query(User).where(User.username == username).first()
        if(user == None):
            print("No account has that name.")
            return
        tweets = db_session.query(Tweet).join(User, User.username == Tweet.username).filter(User.username == user.username).all()
        
        for tweet in tweets:
            print(tweet)

    def search_by_tag(self):
        tag_input = input("Find Tag:")
        tags = db_session.query(Tag).filter(Tag.content == f"#{tag_input}").all()
        if(tags == None):
            print("No such tag exists")
            return
        
        for tag in tags:
            print(tag.tweets) 

    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        init_db()

        print("Welcome to ATCS Twitter!")
        self.startup()
        while(self.logged_in == True):

            self.print_menu()
            option = int(input(""))

            if option == 1:
                self.view_feed()
            elif option == 2:
                self.view_my_tweets()
            elif option == 3:
                self.search_by_tag()
            elif option == 4:
                self.search_by_user()
            elif option == 5:
                self.tweet()
            elif option == 6:
                self.follow()
            elif option == 7:
                self.unfollow()
            else:
                self.logout()
            
        self.end()
