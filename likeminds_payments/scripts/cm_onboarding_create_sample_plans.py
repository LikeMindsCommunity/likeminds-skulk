from subscription.plans.models import SamplePlanCategory, SamplePlan
from subscription.utility.model_utilities import ModelUtilities
from subscription.utility.states import sample_plan_types

import time

sample_plan_category_list = [
    {
        "id": 1,
        "name": "Language Learning",
        "image_url": ""
    },
    {
        "id": 2,
        "name": "Exam preparation",
        "image_url": ""
    },
    {
        "id": 3,
        "name": "Health & fitness",
        "image_url": ""
    },
    {
        "id": 4,
        "name": "Hobby Training",
        "image_url": ""
    },
    {
        "id": 5,
        "name": "Life Coaching",
        "image_url": ""
    },
    {
        "id": 6,
        "name": "Income Generation",
        "image_url": ""
    },
    {
        "id": 7,
        "name": "Professional Skilling",
        "image_url": ""
    },
    {
        "id": 8,
        "name": "Entertainment experiences",
        "image_url": ""
    }
]

sample_plans_list = [
    {
        "id": 1,
        "name": "Monthly Membership",
        "description": """$#Live weekend classes
$#Interview prep
$#Exam Prep
$#Informal conversations with the community
$#1-1 sessions with the mentors
$#Communication skills booster
$#Guest lectures
$#Regular tests""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 1
    },
    {
        "id": 2,
        "name": "Half-Yearly Membership",
        "description": """$#Basic to intermediate French grammar
$#Basic verbal conversations 
$#French with fun activities
$#French culture, food and history
$#Tenses, nouns and verbs
$#Passage, sentences, expressions
$#Letter, essay writing, dialogues,
$#French news and updates""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 1
    },
    {
        "id": 3,
        "name": "Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 1
    },
    {
        "id": 4,
        "name": "Monthly Membership",
        "description": """$#Live weekend classes
$#In depth study material 
$#Over 100 Mock tests
$#Doubt sessions
$#Tips & tricks 
$#Syllabus planning
$#Live webinars with toppers
$#Live test series
$#100+ Video lectures""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 2
    },
    {
        "id": 5,
        "name": "Half-Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 2
    },
    {
        "id": 6,
        "name": "Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 2
    },
    {
        "id": 7,
        "name": "Monthly Membership",
        "description": """$#Support group
$#Live sessions with the psychologists
$#Learn Healthy coping skills
$#Supportive community 
$#4 one-to-one sessions""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 3
    },
    {
        "id": 8,
        "name": "Half-Yearly Membership",
        "description": """$#Daily live meditation session
$#Daily live yoga session
$#Support and motivation from likeminded people
$#Weekly fitness contests
$#4 one-to-one sessions
$#Customised diet plans for gain or lose 
$#Vegan diet plans""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 3
    },
    {
        "id": 9,
        "name": "Yearly Membership",
        "description": """$#Boost natural immunity
$#Improve productivity and focus
$#Yogic diet plan
$#Knowledge sharing sessions 
$#Pre recorded sessions
$#Bonding and rejuvenation meet-ups""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 3
    },
    {
        "id": 10,
        "name": "Monthly Membership",
        "description": """$#14 dance classes per month
$#Small group size
$#History of dance form 
$#Online live performance
$#One on one feedback sessions
$#2 Routines per month 
$#Online Exams
$#Certificate """,
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 4
    },
    {
        "id": 11,
        "name": "Half-Yearly Membership",
        "description": """$#Tutorial on getting started with sketching
$#Introduction to watercolours and acrylic paintings
$#One to one review sessions
$#Art of 3D paining
$#Access to art exhibitions 
$#E-book worth Rs. 499
$#100+ practice worksheets
        """,
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 4
    },
    {
        "id": 12,
        "name": "Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 4
    },
    {
        "id": 13,
        "name": "Monthly Membership",
        "description": """$#Confidence boosting sessions
$#Access to 5 events per month 
$#Practice sessions
$#Mindset training
$#Weekly AMA sessions
$#Art of introspection
$#Goal management 1-1 session""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 5
    },
    {
        "id": 14,
        "name": "Half-Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 5
    },
    {
        "id": 15,
        "name": "Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 5
    },
    {
        "id": 16,
        "name": "Monthly Membership",
        "description": """$#Weekly live sessions
$#Recorded sessions
$#Community discussions
$#Exposure to the experts
$#25% off on one on one consultation
$#50% off on one to one courses
$#Client acquisition training 
$#Freelance job oppurtunities""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 6
    },
    {
        "id": 17,
        "name": "Half-Yearly Membership",
        "description": """$#Collaborations
$#Promotions on our page with 200k followers 
$#Access to global community 
$#One on one sessions 
$#Weekly AMA sessions""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 6
    },
    {
        "id": 18,
        "name": "Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 6
    },
    {
        "id": 19,
        "name": "Monthly Membership",
        "description": """$#Weekly live sessions
$#Career roadmap and consultation
$#Mentorship support
$#Peer to peer learning
$#100+ assignments & case studies
$#Interview preprations
$#Resume review
$#Access to premium seminars""",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 7
    },
    {
        "id": 20,
        "name": "Half-Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 7
    },
    {
        "id": 21,
        "name": "Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 7
    },
    {
        "id": 22,
        "name": "Monthly Membership",
        "description": """$#Daily show access
$#Access to exclusive community 
$#events worth 15k """,
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 1,
        "cost": 200,
        "strike_cost": 300,
        "category_id": 8
    },
    {
        "id": 23,
        "name": "Half-Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 6,
        "cost": 600,
        "strike_cost": 800,
        "category_id": 8
    },
    {
        "id": 24,
        "name": "Yearly Membership",
        "description": "",
        "duration_name": sample_plan_types.MONTHLY,
        "duration_in_months": 12,
        "cost": 1000,
        "strike_cost": 1400,
        "category_id": 8
    }
]


def create_or_update_sample_plan_category():

    for sample_plan_category in sample_plan_category_list:

        sample_plan_category_filter = ModelUtilities.get_model_filter(SamplePlanCategory,
                                                                      {'id': sample_plan_category.get('id')})

        if not sample_plan_category_filter:
            sample_plan_category_instance = SamplePlanCategory.create_instance(sample_plan_category)
            sample_plan_category_instance.save()

        else:
            SamplePlanCategory.update_instance(sample_plan_category_filter[0], sample_plan_category)


def create_or_update_sample_plans():

    for sample_plan in sample_plans_list:

        sample_plan_filter = ModelUtilities.get_model_filter(SamplePlan, {'id': sample_plan.get('id')})

        category_instance = ModelUtilities.get_model_instance_or_none(SamplePlanCategory, sample_plan.get(
            'category_id'))

        sample_plan['category_instance'] = category_instance

        if not sample_plan_filter:
            sample_pan_instance = SamplePlan.create_instance(sample_plan)
            sample_pan_instance.save()

        else:
            SamplePlan.update_instance(sample_plan_filter[0], sample_plan)


started = time.time()
print("Started")
print("Creating or updating sample plan categories")
create_or_update_sample_plan_category()
print("Creating or updating sample plans")
create_or_update_sample_plans()
print("Completed successfully", time.time() - started)
