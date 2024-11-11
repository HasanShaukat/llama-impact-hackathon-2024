# Team New Horizons - Llama Impact Hackathon 2024
Welcome to our project submission repository for the famous Llama Impact Hackathon 2024. Our team, named "New Horizons", has developed a system that processes Kosovo's public complaints for urban conditions, and helps the urban planning team in Kosovo t:
* Understand the bigger picture of all the complaints
* Act on the most severe urban problems

Kosovo is a part of the **FixMyStreet** initiative (https://fixmystreet.org/sites/), and they maintain a website https://ndreqe.com/reports to collect and manage their street complaints from the public. Having this initiative and website set-up, it is a matter of great potential to scale this project to other countries that have a similar initiative running.

## Steps
Our work was done in the following steps:
* Web Scraping
* Data Wrangling
* Llama 3.2 based Translation
* Llama 3.2 based photo description
* Severity Framework definition
* Framework based Complaint Severity Assessment
* Data Visualization on Streamlit
* Chat based further insights on Streamlit

#### Web Scraping
We used a UI based web scraper to fetch all the complaints. The remaining LLM operations unfortunately could not be done on the entire dataset, so we ended up taking the first 100 rows as a sample dataset to test and run our LLM operations

#### Data Wrangling
After fetching the complaints, their times and the user text description from the person submitting the complaint, we parsed the image URLs from the partial image paths, complaint numbers and municipalities from the URLs

#### Translation
After having a tidy dataset, we used the Llama 3.2 90B model to translate the complaint title and text from the native Albanian language to English.  
Translation from the Llama 3.2 11B model was having multiple misinterpretation mistakes. For example, in one complaint the user said that he notified the municipality administration 3 times, while the 11B model translated it to "the municipality will demolish the building in 3 days". Very misleading and incorrect. So we ended up using the 90B model.

#### Image Description
Now that we have the translated complaint title and text, we used both of these fields and the provided images in the complaint to generate a comprehensive text description of the image. Since we used the complaint title and user text, the output description had the right context to describe the image better, as if a reporter is writing notes about the site.

#### Severity Framework
We had to assign the severity of every complaint, so that the urban planning team would solve the most important ones first. But completely relying on an LLM to assign a number to qualitative text and images was not a wise decision, as it would add the LLM's bias and might result in unfair treatment of the soceity based on an AI model. So, to counter that challenge, we ourselves defined the meaning of each severity level (0 to 10) in plain text. The definitions are:
0, Nothing, No issue identified. Example: Complaint lacks validity, or issue is not within the municipality's responsibilities (e.g., a misunderstanding or non-actionable complaint).
1, Minimal, Very low-impact issues that cause no harm or disruption. Example: Aesthetic complaints, like minor graffiti or slightly faded street signs that don’t affect readability or public safety.
2, Very Low, Low-impact issues causing minor inconvenience to individuals but not affecting safety or the community at large. Example: Small amounts of litter on streets, slightly cracked pavement that doesn’t pose an immediate hazard.
3, Low, Minor issues that may require eventual attention but aren’t urgent or disruptive. Example: Overgrown bushes or trees blocking signs, slightly uneven sidewalks in low-traffic areas.
4, Moderate, Issues affecting convenience or aesthetics that need attention but don’t pose an immediate hazard. Example: Broken benches in public parks, moderate graffiti on public property, or minor damage to playground equipment.
5, Noticeable, Issues that start to impact public comfort or have a small effect on functionality. Example: Dim or flickering street lights in residential areas, potholes on local roads that may cause inconvenience but are not a safety threat.
6, Significant, Issues that affect the daily life of residents and may escalate if not addressed within a reasonable timeframe. Example: Roadside litter accumulation, significant sidewalk damage, or low-level flooding in low-traffic areas.
7, High, Problems that impact public safety, comfort, or accessibility, demanding more immediate attention. Example: Large potholes on busy streets, hazardous playground equipment, or broken traffic lights in low-traffic intersections.
8, Very High, Severe issues causing major disruption or potential safety risks, requiring prompt action. Example: Non-functional street lighting in high-crime areas, major potholes on main roads, or sewage overflow in low-traffic areas.
9, Critical, Critical problems with widespread impact, risking safety, health, or infrastructure if not resolved swiftly. Example: Electrical faults in public buildings, significant flooding in residential areas, or hazardous road conditions on main thoroughfares.
10, Emergency, Urgent and life-threatening issues requiring immediate action to prevent injury or catastrophic infrastructure damage. Example: Major flooding affecting homes, downed power lines in public areas, or sewage overflow near high-traffic zones and residential areas.

#### Severity Assessment
Using this definition, we now asked Llama 3.2 90B model as to which level does the individual complaint text and description relate the most. This definition above is an arbitrary start, and Kosovo's urban planning team could improve this definition and have a better severity assessment system because of that.

#### Data Visualization
After assessing the severities of each complaint, it's not time to visualize the data in line, bar, pie charts, and filtering time ranges, complaint categories and municipalities from the filter pane. The urban planning manager could easily see the stats for different issues across different regions, all in one dashboard tab.

#### Chat Conversations with Municipal Complaints Data
The most modern feature of this entire solution is the ability to ask questions about the complaints under consideration. The urban planning manager can use the same filters for time ranges, regions, and complaint topics, and ask the chatbot to create a summary of all the complaints in the filter criteria. Or the user could ask about a specific question, and the chatbot/Copilot would use all the complaints' text to answer the user's question. This way the urban planning managers would get deepar insights and possible solutions quickly about the pressing topics of urban issues.
