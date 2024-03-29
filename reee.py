 def shoot(self, gameName, playerName, table, xvel, yvel):
        # Get the playerID from the playerName using the Database class helper method
        
        playerID = self.database.getPlayerID(playerName)
        
        if playerID is None:
            print(f"Player '{playerName}' not found.")
            return None

        # Create a new entry in the Shot table and get the shotID

        gameID = self.database.getGameID(gameName)

        if gameID is None:
            print(f"Game '{gameName}' not found.")
            return None
        

        shotID = self.database.newShot(playerID, gameID)

        if shotID is None:
            print("Error creating new shot.")
            return None
        

        # Get the cue ball from the table using the Table class helper method
        cue_ball = table.cueBall()
        
        if cue_ball is None:
            print("Cue ball not found on the table.")
            return None

        # Store the current position of the cue ball
        xpos = cue_ball.obj.still_ball.pos.x
        ypos = cue_ball.obj.still_ball.pos.y

        # Set the type attribute of the cue ball to PHYLIB_ROLLING_BALL
        cue_ball.type = phylib.PHYLIB_ROLLING_BALL

        # Set the attributes of the cue ball
        cue_ball.obj.rolling_ball.pos.x = xpos
        cue_ball.obj.rolling_ball.pos.y = ypos
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel
        speed_rb = 0
        # Recalculate the acceleration parameters
        speed_rb = math.sqrt(xvel ** 2 + yvel ** 2)

        # Compute acceleration with drag
        if speed_rb > VEL_EPSILON:
            accx = (-xvel/ speed_rb) * DRAG
            accy = (-yvel / speed_rb) * DRAG
        else:
            accx = 0.0
            accy = 0.0
            
        cue_ball.obj.rolling_ball.acc.x = accx
        cue_ball.obj.rolling_ball.acc.y = accy


        
        
        # Set the number of the cue ball to 0
        cue_ball.obj.rolling_ball.number = 0

        
        

        print(table)
        while table.segment() is not None:
            # Call the segment method to simulate physics for the next time step
            tt = Table.copy_table(table)
            segment_start_time = table.time
            print("Before segment call - table:", table)
            table = table.segment()

            

            if table is None:
                break 
            # Calculate the length of the segment in seconds
            segment_length = round((table.time - segment_start_time) / FRAME_RATE)

            # Display the start and end times for the current segment
            print(f"Segment Start Time: {segment_start_time}, Segment End Time: {table.time}")

            # Loop over the integers representing frames
            for frame_number in range(segment_length):
                # Calculate the time for the current frame
                current_frame_time = segment_start_time + (frame_number * FRAME_RATE)

                # Create a new Table object for the next frame
                frame_table = Table()

                # Iterate over all objects in the original table
                for obj in tt:  # Use the initial_table for iteration
                    if isinstance(obj, RollingBall):
                        # Create a new RollingBall with the same attributes
                        new_ball = RollingBall(
                            obj.obj.rolling_ball.number,
                            Coordinate(obj.obj.rolling_ball.pos.x, obj.obj.rolling_ball.pos.y),
                            Coordinate(obj.obj.rolling_ball.vel.x, obj.obj.rolling_ball.vel.y),
                            Coordinate(obj.obj.rolling_ball.acc.x, obj.obj.rolling_ball.acc.y)
                        )
                        # Call phylib_roll to compute the new position
                        phylib.phylib_roll(new_ball, obj, frame_number* FRAME_RATE)
                        # Add the new ball to the frame table
                        frame_table += new_ball

                    elif isinstance(obj, StillBall):
                        # Create a new StillBall with the same attributes
                        new_ball = StillBall(
                            obj.obj.still_ball.number,
                            Coordinate(obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y)
                        )
                        # Add the new ball to the frame table
                        frame_table += new_ball

                # Set the time of the frame table to the current frame time
                frame_table.time = current_frame_time

                # Save the frame table to the database using writeTable
                table_id = self.database.writeTable(frame_table)

                # Record the table in the TableShot table
                self.database.connection.execute(
                    "INSERT INTO TableShot (SHOTID, TABLEID) VALUES (?, ?)",
                    (shotID, table_id)
                )

            # Update the segment start time for the next iteration
            segment_start_time = table.time


        print(table)
        # Display the total start and end times for the entire shooting process


        # Return the shotID
        return shotID
    