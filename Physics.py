import phylib
import sqlite3
import os
import math
import copy

BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON
DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS
FRAME_RATE = 0.01
HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />"""
FOOTER = """</svg>\n"""

BALL_COLOURS = [
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",
    "MEDIUMPURPLE",
    "LIGHTSALMON",
    "LIGHTGREEN",
    "SANDYBROWN",
]

class Coordinate(phylib.phylib_coord):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass

class StillBall(phylib.phylib_object):
    """
    Python StillBall class.
    """

    def __init__(self, number, pos):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_STILL_BALL,
                                       number,
                                       pos, None, None,
                                       0.0, 0.0)

        self.__class__ = StillBall

    def svg(self):
        """
        Method to generate SVG representation of the still ball.
        """
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, 28.5, BALL_COLOURS[self.obj.still_ball.number])

class RollingBall(phylib.phylib_object):
    """
    Python RollingBall class.
    """

    def __init__(self, number, pos, vel, acc):
        """
        Constructor function. Requires ball number, position (x,y), velocity (vx,vy),
        and acceleration (ax,ay) as arguments.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_ROLLING_BALL,
                                       number,
                                       pos,
                                       vel,
                                       acc, 0.0, 0.0)

        self.__class__ = RollingBall

    def svg(self):
        """
        Method to generate SVG representation of the rolling ball.
        """
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, 28.5, BALL_COLOURS[self.obj.rolling_ball.number])

class Hole(phylib.phylib_object):
    """
    Python Hole class.
    """

    def __init__(self, pos):
        """
        Constructor function. Requires position (x,y) as argument.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_HOLE,
                                       None,
                                       pos,
                                       None, None, 0.0, 0.0)

        self.__class__ = Hole
        
    def svg(self):
        """
        Method to generate SVG representation of the hole.
        """
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x , self.obj.hole.pos.y, HOLE_RADIUS)
class HCushion(phylib.phylib_object):
    """
    Python HCushion class.
    """

    def __init__(self, y):
        """
        Constructor function. Requires y-coordinate as argument.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_HCUSHION,
                                       None,
                                       None,
                                       None, None, 0.0, y)
        self.__class__ = HCushion

    def svg(self):
       return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % (self.obj.hcushion.y) 

class VCushion(phylib.phylib_object):
    """
    Python VCushion class.
    """

    def __init__(self, x):
        """
        Constructor function. Requires x-coordinate as argument.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_VCUSHION,
                                       None,
                                       None,
                                       None, None, x, 0.0)
        self.__class__ = VCushion

    def svg(self):
        """
        Method to generate SVG representation of the vertical cushion.
        """
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % (self.obj.vcushion.x)

class Table(phylib.phylib_table):
    """
    Pool table class.
    """

    def __init__(self):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__(self)
        self.current = -1

    def __iadd__(self, other):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object(other)
        return self

    def __iter__(self):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self

    def __next__(self):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1  # increment the index to the next object
        if self.current < MAX_OBJECTS:  # check if there are no more objects
            return self[self.current]  # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1  # reset the index counter
        raise StopIteration  # raise StopIteration to tell for loop to stop

    def __getitem__(self, index):
        """
        This method adds item retrieval support using square brackets [ ] .
        It calls get_object (see phylib.i) to retrieve a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object(index)
        if result == None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__(self):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = ""  # create empty string
        result += "time = %6.1f;\n" % self.time  # append time
        for i, obj in enumerate(self):  # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i, obj)  # append object description
        return result  # return the string

    def segment(self):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment(self)
        if result:
            result.__class__ = Table
            result.current = -1
        return result

    def svg(self):
        """
        Method to generate SVG representation of the table.
        """
        svg_string = HEADER
        for obj in self:
            if obj is not None:  # Add this check to handle None objects
                svg_string += obj.svg()
        svg_string += FOOTER
        return svg_string
    
    def roll( self, t ):
        new = Table();
        for ball in self:
            if isinstance( ball, RollingBall ):
                # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number,
                            Coordinate(ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y),
                            Coordinate(ball.obj.rolling_ball.vel.x, ball.obj.rolling_ball.vel.y),
                            Coordinate(ball.obj.rolling_ball.acc.x, ball.obj.rolling_ball.acc.y))
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t );
                # add ball to table
                new += new_ball;
            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number,
                Coordinate( ball.obj.still_ball.pos.x,
                ball.obj.still_ball.pos.y ) );
                # add ball to table
                new += new_ball;
        # return table
        return new;

    def cueBall(self):
        """
        Method to find the cue ball (ball number 0) in the table.
        """
        for ball in self:
            if isinstance(ball, StillBall) and ball.obj.still_ball.number == 0:
                return ball
            if isinstance(ball, RollingBall) and ball.obj.rolling_ball.number == 0:
                return ball
        return None
    
    def copy_object(dest, src):
        if src is None:
            dest = None
        else:
            dest = copy.deepcopy(src)

    def copy(table):
        if table is None:
            return None

        new_table = {
            "time": table["time"],
            "object": [None] * len(table["object"])
        }

        for i, obj in enumerate(table["object"]):
            if obj is not None:
              table.copy_object(new_table["object"][i],obj)
            else:
                new_table["object"][i] = None

        return new_table
    


class Database():

    
        def __init__(self, reset=False):
            # Check if reset is True, and if so, delete the existing database file
            if reset:
                try:
                    os.remove("phylib.db")
                except FileNotFoundError:
                    pass  # Ignore if the file doesn't exist

            # Establish a conn to the SQLite database file
            self.conn = sqlite3.connect("phylib.db")

        def createDB(self):
            cursor = self.conn.cursor()

            # Check if Ball table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Ball'")
            ball_table_exists = cursor.fetchone()
            if not ball_table_exists:
                cursor.execute('''CREATE TABLE Ball (
                                    BALLID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    BALLNO INTEGER NOT NULL,
                                    XPOS FLOAT NOT NULL,
                                    YPOS FLOAT NOT NULL,
                                    XVEL FLOAT,
                                    YVEL FLOAT
                                )''')

            # Check if TTable table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TTable'")
            billiards_table_exists = cursor.fetchone()
            if not billiards_table_exists:
                cursor.execute('''CREATE TABLE TTable (
                                    TABLEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    TIME FLOAT NOT NULL
                                )''')

            # Check if BallTable table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='BallTable'")
            ball_table_table_exists = cursor.fetchone()
            if not ball_table_table_exists:
                cursor.execute('''CREATE TABLE BallTable (
                                    BALLID INTEGER NOT NULL,
                                    TABLEID INTEGER NOT NULL,
                                    FOREIGN KEY (BALLID) REFERENCES Ball (BALLID),
                                    FOREIGN KEY (TABLEID) REFERENCES TTable (TABLEID)
                                )''')

            # Check if Shot table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Shot'")
            shot_table_exists = cursor.fetchone()
            if not shot_table_exists:
                cursor.execute('''CREATE TABLE Shot (
                                   SHOTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                   PLAYERID INTEGER NOT NULL,
                                   GAMEID INTEGER NOT NULL,
                                   FOREIGN KEY (PLAYERID) REFERENCES Player,
                                   FOREIGN KEY (GAMEID) REFERENCES Game
                                );
                            ''')
            # Check if TableShot table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TableShot'")
            table_shot_table_exists = cursor.fetchone()
            if not table_shot_table_exists:
                cursor.execute('''CREATE TABLE TableShot (
                                   SHOTID INTEGER NOT NULL,
                                   TABLEID INTEGER NOT NULL,
                                   FOREIGN KEY (TABLEID) REFERENCES TTable,
                                   FOREIGN KEY (SHOTID) REFERENCES Shot
                                );
                            ''')

            # Check if Game table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Game'")
            game_table_exists = cursor.fetchone()
            if not game_table_exists:
                cursor.execute('''CREATE TABLE Game (
                                   GAMEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                   GAMENAME VARCHAR(64) NOT NULL
                                );
                            ''')

            # Check if Player table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Player'")
            player_table_exists = cursor.fetchone()
            if not player_table_exists:
                cursor.execute('''CREATE TABLE Player (
                                     PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                     GAMEID INTEGER NOT NULL,
                                     PLAYERNAME VARCHAR(64) NOT NULL,
                                     FOREIGN KEY (GAMEID) REFERENCES Game
                                );
                            ''')

            self.conn.commit()
           
            cursor.close()  # Close the cursor

        def readTable(self, tableID):
            cursor = self.conn.cursor()

            # Use a single SQL SELECT statement with a JOIN clause to retrieve data
            cursor.execute("""SELECT Ball.BALLNO, Ball.XPOS, Ball.YPOS, Ball.XVEL, Ball.YVEL
                            FROM Ball
                            INNER JOIN BallTable ON Ball.BALLID = BallTable.BALLID
                            WHERE BallTable.TABLEID = ?""", (tableID + 1,))  # Increment tableID by 1 to match SQL numbering

            # Fetch all rows from the query result
            rows = cursor.fetchall()

            # If no rows are fetched, return None
            if not rows:
                cursor.close()
                return None

            # Initialize a Table object with standard holes and cushions
            table = Table()

            # Retrieve the table's time attribute from the TTable table
            cursor.execute("SELECT TIME FROM TTable WHERE TABLEID = ?", (tableID + 1,))
            time = cursor.fetchone()[0]  # Fetch the first column of the first row

            # Iterate over the fetched rows and instantiate balls accordingly
            for row in rows:
                ballNo, xPos, yPos, xVel, yVel = row
                if xVel is None and yVel is None:
                    # Instantiate StillBall if velocity components are None
                    ball = StillBall(ballNo, Coordinate(xPos, yPos))
                else:
                    # Calculate acceleration with drag
                    rb_dx = xVel
                    rb_dy = yVel
                    speed_rb = math.sqrt(rb_dx ** 2 + rb_dy ** 2)

                    # Compute acceleration with drag
                    if speed_rb > VEL_EPSILON:  # A very small value to handle division by zero
                        acceleration_x = -rb_dx / speed_rb * DRAG  # DRAG constant
                        acceleration_y = -rb_dy / speed_rb * DRAG  # DRAG constant
                    else:
                        acceleration_x = 0.0
                        acceleration_y = 0.0
                    
                    # Instantiate RollingBall with calculated acceleration
                    ball = RollingBall(ballNo, Coordinate(xPos, yPos), Coordinate(xVel, yVel), Coordinate(acceleration_x, acceleration_y))

                # Add the instantiated ball to the Table
                table.add_object(ball)

            # Set the time attribute of the table
            table.time = time

            # Close cursor and commit changes
            cursor.close()
            self.conn.commit()

            return table


        def writeTable(self, table):
            cursor = self.conn.cursor()

            cursor.execute("INSERT INTO TTable (TIME) VALUES (?)", (table.time,))
            table_id = cursor.lastrowid - 1
            print(table_id)
            # Insert objects into Ball table and associate with the current table
            for obj in table:
                if isinstance(obj, StillBall):
                    cursor.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS) VALUES (?, ?, ?)", (obj.obj.still_ball.number, obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y))
                     # Get the autoincremented BALLID value
                    ballID = cursor.lastrowid 
                    # Associate the ball with the current table
                    cursor.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ballID,table_id + 1))
                    
                elif isinstance(obj, RollingBall):
                    cursor.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                        (obj.obj.rolling_ball.number, obj.obj.rolling_ball.pos.x, obj.obj.rolling_ball.pos.y,
                                            obj.obj.rolling_ball.vel.x, obj.obj.rolling_ball.vel.y))
                    ballID = cursor.lastrowid 

                    # Associate the ball with the current table
                    cursor.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ballID,table_id + 1))


                    # Close cursor and commit changes  
                    self.conn.commit()
                    cursor.close
             # Return the auto-incremented TABLEID value minus 1
            return table_id 
                
        def close(self):
            # Commit changes and close the database conn
            self.conn.commit()
            self.conn.close()

        def newShot(self, gameName, playerName):
            cursor = self.conn.cursor()

             # Get the gameID for the provided gameName
            cursor.execute("SELECT GAMEID FROM Game WHERE GAMENAME = ?", (gameName,))
            game_record = cursor.fetchone()
            if game_record is None:
                raise ValueError(f"No game found with name: {gameName}")
            gameID = game_record[0]

            # Get the playerID for the provided playerName
            cursor.execute("SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?", (playerName,))
            player_record = cursor.fetchone()
            if player_record is None:
                raise ValueError(f"No player found with name: {playerName}")
            playerID = player_record[0]

            # Insert a new entry into the Shot table
            cursor.execute("INSERT INTO Shot (GAMEID, PLAYERID) VALUES (?, ?)", (gameID, playerID))
            shotID = cursor.lastrowid

            # Close cursor and commit changes
            cursor.close()
            self.conn.commit()

            return shotID
        

        def getGame(self, gameID):
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT G.GAMEID, G.GAMENAME, P1.PLAYERNAME AS PLAYER1NAME, P2.PLAYERNAME AS PLAYER2NAME
                FROM Game G
                JOIN Player P1 ON G.PLAYER1ID = P1.PLAYERID
                JOIN Player P2 ON G.PLAYER2ID = P2.PLAYERID
                WHERE G.GAMEID = ?
            """, (gameID,))
            game_info = cursor.fetchone()
            cursor.close()
            if game_info:
                return {
                    'gameID': game_info[0],
                    'gameName': game_info[1],
                    'player1Name': game_info[2],
                    'player2Name': game_info[3]
                }
            else:
                raise ValueError(f"No game found with gameID {gameID}.")



        def setGame(self, gameName, player1Name, player2Name):
            cursor = self.conn.cursor()
            
            # Insert game information into Game table
            cursor.execute("INSERT INTO Game (GAMENAME) VALUES (?)", (gameName,))
            gameID = cursor.lastrowid  # Retrieve the auto-generated game ID
            
            # Insert player1Name into Player table with the associated gameID
            cursor.execute("INSERT INTO Player (PLAYERNAME, GAMEID) VALUES (?, ?)", (player1Name, gameID))
            player1ID = cursor.lastrowid
            
            # Insert player2Name into Player table with the associated gameID
            cursor.execute("INSERT INTO Player (PLAYERNAME, GAMEID) VALUES (?, ?)", (player2Name, gameID))
            player2ID = cursor.lastrowid
            
            # Commit changes and close cursor
            self.conn.commit()
            cursor.close()
class Game:
    
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        self.db = Database( reset=True );
        db = self.db
        db.createDB();
        self.conn = sqlite3.connect("phylib.db")
        if gameID is not None and gameName is None and player1Name is None and player2Name is None:
           new_game =  db.getGame(gameID)
           self.gameName = new_game['gameName']
           self.player1Name = new_game['player1Name']
           self.player2Name = new_game['player2Name']
        elif gameID is None and isinstance(gameName, str) and isinstance(player1Name, str) and isinstance(player2Name, str):
            self.gameID = None
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
            db.setGame(self.gameName,self.player1Name,self.player2Name)
            
        else:
            raise TypeError("Invalid combination of arguments provided to the constructor")


    def shoot(self, gameName, playerName, table, xvel, yvel):
        shotID = self.db.newShot(gameName, playerName)
        cue_ball = table.cueBall()

        if cue_ball is None:
            print("Error: Cue ball not found")
            return

        xpos, ypos = cue_ball.obj.rolling_ball.pos.x, cue_ball.obj.rolling_ball.pos.y
        cue_ball.type = phylib.PHYLIB_ROLLING_BALL
        cue_ball.obj.rolling_ball.pos.x = xpos
        cue_ball.obj.rolling_ball.pos.y = ypos
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel

        acceleration_x, acceleration_y = self.calculateAcceleration(xvel, yvel, VEL_EPSILON, DRAG)        
        cue_ball.obj.rolling_ball.acc.x = acceleration_x
        cue_ball.obj.rolling_ball.acc.y = acceleration_y
        cue_ball.obj.rolling_ball.number = 0
  
        while table is not None:
            newt_table = table
            startTime = table.time
            table = table.segment()

            if table is None:
                break

            segment_length = round((table.time - startTime) / FRAME_RATE)

            for i in range(segment_length):
                new_table = Table()
                time_offset = i * FRAME_RATE
                new_table = newt_table.roll(time_offset)  # Use newt_table, not table
                new_table.time = startTime + time_offset
                print(new_table)
                new_table_id = self.db.writeTable(new_table)
                self.db.conn.execute("INSERT INTO TableShot (SHOTID, TABLEID) VALUES (?, ?)", (shotID, new_table_id))
                self.db.conn.commit()


            # table = next_table


    
    
    
    def calculateAcceleration(self,rb_dx, rb_dy, VEL_EPSILON, DRAG):
        # Compute the speed of the rolling ball
        # Recalculate acceleration parameters
        speed_rb = math.sqrt(rb_dx ** 2 + rb_dy ** 2)

        # Compute acceleration with drag
        if speed_rb > 0.01:
            acceleration_x = rb_dx / speed_rb * 150.0
            acceleration_y = rb_dy / speed_rb * 150.0
        else:
            acceleration_x = 0.0
            acceleration_y = 0.0
        return acceleration_x, acceleration_y

    
        