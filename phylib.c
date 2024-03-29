#include "phylib.h"

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos)
{
    // Allocate memory for phylib_object
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));

    // Check for allocation failure
    if (new_object == NULL)
    {
        fprintf(stderr, "Memory allocation failed for phylib_object.\n");
        return NULL;
    }

    // Set the type of the new object
    new_object->type = PHYLIB_STILL_BALL;

    // Initialize the still_ball object within the phylib_untyped union
    new_object->obj.still_ball.number = number;
    new_object->obj.still_ball.pos = *pos;

    return new_object;
}

phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_object == NULL)
    {
        fprintf(stderr, "Memory allocation failed for phylib_object.\n");
        return NULL;
    }

    new_object->type = PHYLIB_ROLLING_BALL;
    new_object->obj.rolling_ball.number = number;
    new_object->obj.rolling_ball.pos = *pos;
    new_object->obj.rolling_ball.vel = *vel;
    new_object->obj.rolling_ball.acc = *acc;

    return new_object;
}

phylib_object *phylib_new_hole(phylib_coord *pos)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_object == NULL)
    {
        fprintf(stderr, "Memory allocation failed for phylib_object.\n");
        return NULL;
    }

    new_object->type = PHYLIB_HOLE;
    new_object->obj.hole.pos = *pos;

    return new_object;
}

phylib_object *phylib_new_hcushion(double y)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_object == NULL)
    {
        fprintf(stderr, "Memory allocation failed for phylib_object.\n");
        return NULL;
    }

    new_object->type = PHYLIB_HCUSHION;
    new_object->obj.hcushion.y = y;

    return new_object;
}

phylib_object *phylib_new_vcushion(double x)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));

    if (new_object == NULL)
    {
        fprintf(stderr, "Memory allocation failed for phylib_object.\n");
        return NULL;
    }

    new_object->type = PHYLIB_VCUSHION;
    new_object->obj.vcushion.x = x;

    return new_object;
}

phylib_table *phylib_new_table(void)
{
    // Allocate memory for the table structure
    phylib_table *table = (phylib_table *)malloc(sizeof(phylib_table));

    // Check for memory allocation failure
    if (table == NULL)
    {
        return NULL;
    }

    table->time = 0.0;
    table->object[0] = phylib_new_hcushion(0.0);
    table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
    table->object[2] = phylib_new_vcushion(0.0);
    table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);

    // Add holes at the four corners
    table->object[4] = phylib_new_hole(&(phylib_coord){0.0, 0.0});
    table->object[5] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_WIDTH});
    table->object[6] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_LENGTH});
    table->object[7] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, 0.0});

    // Add two holes midway between top and bottom holes
    table->object[8] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_WIDTH});
    table->object[9] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH});

    // Set remaining pointers to NULL
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        table->object[i] = NULL;
    }
    return table;
}

void phylib_copy_object(phylib_object **dest, phylib_object **src)
{
    // Check if src points to a NULL pointer
    if (*src == NULL)
    {
        // If src is NULL, assign NULL to dest
        *dest = NULL;
    }
    else
    {
        // Allocate new memory for phylib_object
        *dest = (phylib_object *)malloc(sizeof(phylib_object));

        // Check for memory allocation failure
        if (*dest == NULL)
        {
            // Handle memory allocation failure if needed
            // For now, assign NULL to dest and return

            return;
        }

        // Use memcpy to copy the contents of the object
        memcpy(*dest, *src, sizeof(phylib_object));

        // Save the address of the new object at the location pointed to by dest
    }
}

phylib_table *phylib_copy_table(phylib_table *table)
{
    if (table == NULL)
    {
        return NULL;
    }
    phylib_table *new_table;
    new_table = (phylib_table *)malloc(sizeof(phylib_table));

    if (new_table == NULL)
    {

        return NULL;
    }
    new_table->time = table->time;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        if (table->object[i] != NULL)
        {
            phylib_copy_object(&(new_table->object[i]), &(table->object[i]));
        }
        else
        {
            new_table->object[i] = NULL;
        }
    }

    return new_table;
}

void phylib_add_object(phylib_table *table, phylib_object *object)
{
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
    {
        // Check if the current pointer is NULL
        if (table->object[i] == NULL)
        {

            table->object[i] = object;
            return;
        }
    }
}

void phylib_free_table(phylib_table *table)
{
    if (table != NULL)
    {
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
        {
            phylib_object *temp = table->object[i];
            free(temp);

            table->object[i] = NULL;
        }
    }
    free(table);
}

phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2)
{
    phylib_coord sub_cords;

    // Calculate the differences directly
    sub_cords.x = c1.x - c2.x;
    sub_cords.y = c1.y - c2.y;

    return sub_cords;
}

double phylib_length(phylib_coord c)
{
    double z = 0.0;
    z = sqrt(c.x * c.x + c.y * c.y);

    return z;
}

double phylib_dot_product(phylib_coord a, phylib_coord b)
{
    double z = 0.0;
    z = a.x * b.x + a.y * b.y;

    return z;
}

double phylib_distance(phylib_object *obj1, phylib_object *obj2)
{
    // Check if obj1 is a PHYLIB_ROLLING_BALL
    if (obj1->type != PHYLIB_ROLLING_BALL)
    {
        return -1.0; // obj1 is not a PHYLIB_ROLLING_BALL
    }

    phylib_rolling_ball *rollingBall1 = &(obj1->obj.rolling_ball);

    // Check if obj2 is another BALL (ROLLING or STILL)
    if (obj2->type == PHYLIB_ROLLING_BALL || obj2->type == PHYLIB_STILL_BALL)
    {
        phylib_coord pos1 = rollingBall1->pos;
        phylib_coord pos2;

        if (obj2->type == PHYLIB_ROLLING_BALL)
        {
            pos2 = obj2->obj.rolling_ball.pos;
        }
        else
        {
            pos2 = obj2->obj.still_ball.pos;
        }

        // Compute the distance between the centers of the two balls and subtract two radii
        double distance = sqrt(pow(pos1.x - pos2.x, 2) + pow(pos1.y - pos2.y, 2)) - PHYLIB_BALL_DIAMETER;

        return distance;
    }
    else if (obj2->type == PHYLIB_HOLE)
    {
        phylib_coord pos1 = rollingBall1->pos;
        phylib_coord pos2 = obj2->obj.hole.pos;

        // Compute the distance between the center of the ball and the hole and subtract the HOLE_RADIUS
        double distance = sqrt(pow(pos1.x - pos2.x, 2) + pow(pos1.y - pos2.y, 2)) - PHYLIB_HOLE_RADIUS;

        return distance;
    }
    else if (obj2->type == PHYLIB_HCUSHION || obj2->type == PHYLIB_VCUSHION)
    {
        double ballRadius = PHYLIB_BALL_RADIUS;

        // Calculate the distance between the center of the ball and the cushion and subtract the BALL_RADIUS
        double distance;
        if (obj2->type == PHYLIB_HCUSHION)
        {
            double cushionY = obj2->obj.hcushion.y;
            distance = fabs(rollingBall1->pos.y - cushionY) - ballRadius;
        }
        else
        {
            double cushionX = obj2->obj.vcushion.x;
            distance = fabs(rollingBall1->pos.x - cushionX) - ballRadius;
        }

        return distance;
    }

    // obj2 is not a BALL (ROLLING or STILL)
    return -1.0;
}

void phylib_roll(phylib_object *new, phylib_object *old, double time)
{
    // Check if new and old are PHYLIB_ROLLING_BALLs
    if (new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL)
    {
        return; // Do nothing if not PHYLIB_ROLLING_BALLs
    }

    phylib_rolling_ball *newBall = &(new->obj.rolling_ball);
    phylib_rolling_ball *oldBall = &(old->obj.rolling_ball);

    // Update position using kinematic equation for position
    newBall->pos.x = oldBall->pos.x + oldBall->vel.x * time + 0.5 * oldBall->acc.x * time * time;
    newBall->pos.y = oldBall->pos.y + oldBall->vel.y * time + 0.5 * oldBall->acc.y * time * time;

    // Update velocity using kinematic equation for velocity
    newBall->vel.x = oldBall->vel.x + oldBall->acc.x * time;
    newBall->vel.y = oldBall->vel.y + oldBall->acc.y * time;

    // Check for a change in sign of velocity in the x-direction
    if ((oldBall->vel.x * newBall->vel.x) < 0)
    {
        newBall->vel.x = 0.0;
        newBall->acc.x = 0.0;
    }

    // Check for a change in sign of velocity in the y-direction
    if ((oldBall->vel.y * newBall->vel.y) < 0)
    {
        newBall->vel.y = 0.0;
        newBall->acc.y = 0.0;
    }
}

unsigned char phylib_stopped(phylib_object *object)
{
    // Check if object is a PHYLIB_ROLLING_BALL
    if (object->type != PHYLIB_ROLLING_BALL)
    {
        return 0; // Object is not a rolling ball
    }

    // Calculate the speed (length of velocity vector)
    double speed = sqrt(pow(object->obj.rolling_ball.vel.x, 2) + pow(object->obj.rolling_ball.vel.y, 2));

    // Check if the ball has stopped
    if (speed < PHYLIB_VEL_EPSILON)
    {
        // Convert the ball to a STILL_BALL
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos = object->obj.rolling_ball.pos;

        return 1; // Conversion successful
    }

    return 0; // Ball has not stopped
}

void phylib_bounce(phylib_object **a, phylib_object **b)
{
    // phylib_coord r_ab;
    // phylib_coord v_rel;
    //  double length_r_ab;
    switch ((*b)->type)
    {
    case PHYLIB_HCUSHION:
        // Reverse y velocity and acceleration of a
        (*a)->obj.rolling_ball.vel.y = -(*a)->obj.rolling_ball.vel.y;
        (*a)->obj.rolling_ball.acc.y = -(*a)->obj.rolling_ball.acc.y;
        break;

    case PHYLIB_VCUSHION:
        // Reverse x velocity and acceleration of a
        (*a)->obj.rolling_ball.vel.x = -(*a)->obj.rolling_ball.vel.x;
        (*a)->obj.rolling_ball.acc.x = -(*a)->obj.rolling_ball.acc.x;
        break;

    case PHYLIB_HOLE:
        // Free the memory of a and set it to NULL
        free(*a);
        *a = NULL;
        break;

    case PHYLIB_STILL_BALL:
        // Upgrade the STILL_BALL to a ROLLING_BALL
        (*b)->type = PHYLIB_ROLLING_BALL;
        (*b)->obj.rolling_ball.number = (*b)->obj.still_ball.number;
        (*b)->obj.rolling_ball.acc.x = 0.0;
        (*b)->obj.rolling_ball.acc.y = 0.0;
        (*b)->obj.rolling_ball.vel.x = 0.0;
        (*b)->obj.rolling_ball.vel.y = 0.0;
        (*b)->obj.rolling_ball.pos = (*b)->obj.still_ball.pos;

        // ... (you may need to initialize other attributes of rolling ball)

    case PHYLIB_ROLLING_BALL:
    {
        // Compute the position of a with respect to b
        phylib_coord r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);

        // Compute the relative velocity of a with respect to b
        phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);

        // Divide the x and y components of r_ab by the length of r_ab to get the normal vector, n
        double length_r_ab = phylib_length(r_ab);
        phylib_coord n;
        n.x = r_ab.x / length_r_ab;
        n.y = r_ab.y / length_r_ab;

        // Calculate the ratio of the relative velocity v_rel in the direction of ball a
        double v_rel_n = phylib_dot_product(v_rel, n);

        // Update velocities
        (*a)->obj.rolling_ball.vel.x -= v_rel_n * n.x;
        (*a)->obj.rolling_ball.vel.y -= v_rel_n * n.y;

        (*b)->obj.rolling_ball.vel.x += v_rel_n * n.x;
        (*b)->obj.rolling_ball.vel.y += v_rel_n * n.y;

        // Calculate speeds
        double speed_a = phylib_length((*a)->obj.rolling_ball.vel);
        double speed_b = phylib_length((*b)->obj.rolling_ball.vel);

        // Set acceleration of the balls if the speed is greater than PHYLIB_VEL_EPSILON
        if (speed_a > PHYLIB_VEL_EPSILON)
        {
            (*a)->obj.rolling_ball.acc.x = -(*a)->obj.rolling_ball.vel.x / speed_a * PHYLIB_DRAG;
            (*a)->obj.rolling_ball.acc.y = -(*a)->obj.rolling_ball.vel.y / speed_a * PHYLIB_DRAG;
        }

        if (speed_b > PHYLIB_VEL_EPSILON)
        {
            (*b)->obj.rolling_ball.acc.x = -(*b)->obj.rolling_ball.vel.x / speed_b * PHYLIB_DRAG;
            (*b)->obj.rolling_ball.acc.y = -(*b)->obj.rolling_ball.vel.y / speed_b * PHYLIB_DRAG;
        }
    }
    break;
    }
}
unsigned char phylib_rolling(phylib_table *t)
{
    if (t == NULL)
    {
        return 0;
    }

    unsigned char rollingCount = 0;

    // Iterate through the objects in the table
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        phylib_object *currentObject = t->object[i];

        // Check if the object is a ROLLING_BALL
        if (currentObject != NULL && currentObject->type == PHYLIB_ROLLING_BALL)
        {
            rollingCount++;
        }
    }

    return rollingCount;
}

phylib_table *phylib_segment(phylib_table *table)
{
    if (table == NULL)
    {
        return NULL;
    }

    int rollingBallsCount = phylib_rolling(table);

    phylib_table *resultTable = phylib_copy_table(table);
    double currentTime = PHYLIB_SIM_RATE;
    if (rollingBallsCount > 0)
    {
        while (currentTime <= PHYLIB_MAX_TIME)
        {
            update_rolling_balls(resultTable, table, currentTime);

            if (check_stopped_condition(resultTable))
            {
                return resultTable; // Stopping condition 1: Ball has stopped
            }

            if (check_collision_condition(resultTable))
            {
                return resultTable; // Stopping condition 2: Collision detected and bounce applied
            }

            currentTime += PHYLIB_SIM_RATE;
            resultTable->time += PHYLIB_SIM_RATE; // Time update
        }
    }
    phylib_free_table(resultTable);
    return NULL; // Max time reached
}

void update_rolling_balls(phylib_table *resultTable, const phylib_table *table, double currentTime)
{
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
    {
        if (resultTable->object[i] != NULL && resultTable->object[i]->type == PHYLIB_ROLLING_BALL)
        {
            phylib_roll(resultTable->object[i], table->object[i], currentTime);
        }
    }
}

int check_stopped_condition(const phylib_table *resultTable)
{
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
    {
        if (resultTable->object[i] != NULL && resultTable->object[i]->type == PHYLIB_ROLLING_BALL && phylib_stopped(resultTable->object[i]))
        {
            return 1; // Ball has stopped
        }
    }
    return 0;
}

int check_collision_condition(const phylib_table *resultTable)
{
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
    {
        for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++)
        {
            if (i != j && resultTable->object[i] != NULL && resultTable->object[i]->type == PHYLIB_ROLLING_BALL)
            {
                if (resultTable->object[j] != NULL && resultTable->object[i] != resultTable->object[j])
                {
                    if (phylib_distance(resultTable->object[i], resultTable->object[j]) < 0.0)
                    {
                        phylib_bounce((phylib_object **)&resultTable->object[i], (phylib_object **)&resultTable->object[j]);
                        return 1; // Collision detected and bounce applied
                    }
                }
            }
        }
    }
    return 0;
}

char *phylib_object_string(phylib_object *object)
{
    static char string[80];
    if (object == NULL)
    {
        snprintf(string, 80, "NULL;");
        return string;
    }
    switch (object->type)
    {
    case PHYLIB_STILL_BALL:
        snprintf(string, 80,
                 "STILL_BALL (%d,%6.1lf,%6.1lf)",
                 object->obj.still_ball.number,
                 object->obj.still_ball.pos.x,
                 object->obj.still_ball.pos.y);
        break;
    case PHYLIB_ROLLING_BALL:
        snprintf(string, 80,
                 "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                 object->obj.rolling_ball.number,
                 object->obj.rolling_ball.pos.x,
                 object->obj.rolling_ball.pos.y,
                 object->obj.rolling_ball.vel.x,
                 object->obj.rolling_ball.vel.y,
                 object->obj.rolling_ball.acc.x,
                 object->obj.rolling_ball.acc.y);
        break;

    case PHYLIB_HOLE:
        snprintf(string, 80,
                 "HOLE (%6.1lf,%6.1lf)",
                 object->obj.hole.pos.x,
                 object->obj.hole.pos.y);
        break;
    case PHYLIB_HCUSHION:
        snprintf(string, 80,
                 "HCUSHION (%6.1lf)",
                 object->obj.hcushion.y);
        break;
    case PHYLIB_VCUSHION:
        snprintf(string, 80,
                 "VCUSHION (%6.1lf)",
                 object->obj.vcushion.x);
        break;
    }
    return string;
}

