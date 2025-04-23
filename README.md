# FoodieSpot AI Reservation Agent

A full-stack Python application that provides an AI-powered restaurant reservation system using Streamlit for the frontend and Gemini API for conversational AI.

**✨ Live Demo:** [**https://bookfoodiespot.streamlit.app/**](https://bookfoodiespot.streamlit.app/)

## Challenge Overview

This project demonstrates the implementation of an intelligent AI reservation agent for restaurants. The system allows users to search for restaurants, get information about them, check availability, and make reservations through a natural language conversation interface powered by Gemini's large language model.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Gemini API key (Get yours at [Google AI Studio](https://makersuite.google.com/))
- Anaconda or Miniconda (for conda setup)

### Installation

#### Standard Setup:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd foodiespot_reservation_agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   *(You can obtain an API key from [Google AI Studio](https://makersuite.google.com/))*.

4. Run the application:
   ```bash
   cd src
   streamlit run app.py
   ```

#### Conda Environment Setup:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd foodiespot_reservation_agent
   ```

2. Create a new conda environment:
   ```bash
   conda create -n foodiespot python=3.9
   ```

3. Activate the environment:
   ```bash
   conda activate foodiespot
   ```

4. Install the requirements using pip:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   *(You can obtain an API key from [Google AI Studio](https://makersuite.google.com/))*.

6. Run the application:
   ```bash
   cd src
   streamlit run app.py
   ```

## Prompt Engineering Approach

The system prompt for the Gemini model is carefully designed to:

1. Establish the agent's persona as FoodieSpot's friendly reservation assistant
2. Define clear goals for the agent (help users find restaurants, provide information, check availability, make reservations)
3. Set guidelines for behavior (be friendly, use tools appropriately, ask for clarification when needed)
4. Guide the conversation flow from understanding requests to executing appropriate actions
5. Encourage helpful, conversational responses

Tool definitions are provided to the model with clear descriptions and parameter explanations, allowing the LLM to understand when and how to use each tool. The tool schemas include:

- `list_restaurants`: For searching and filtering restaurants
- `get_restaurant_details`: For retrieving detailed information about a specific restaurant
- `check_availability`: For checking if a reservation is possible
- `make_reservation`: For booking a table at a restaurant

This approach leverages Gemini's function-calling capabilities to maintain a clear separation between the LLM's natural language understanding and the execution of specific business logic.

## Tool Calling Implementation

The tool calling architecture is implemented through the following flow:

1. **User Intent Recognition**: The LLM determines the user's intent from their natural language message.
2. **Tool Selection**: Based on the recognized intent, the LLM decides which tool to use and what parameters to provide.
3. **Function Execution**: The agent receives the tool call, executes the corresponding Python function, and retrieves the result.
4. **Result Interpretation**: The tool output is sent back to the LLM, which interprets the results and formulates a natural language response.
5. **Response Generation**: The agent presents the information to the user in a conversational manner.

This approach allows the LLM to handle the complexity of natural language understanding while delegating specific actions to well-defined functions, resulting in a system that is both flexible in conversation and reliable in executing specific tasks.

## Business Strategy Summary

### Key Business Problems & Opportunities

**Problems:**
- Restaurant reservation processes are often manual, time-consuming, and error-prone
- Staff spend significant time on the phone taking reservations
- Customers face friction when making reservations outside business hours
- Restaurants struggle to optimize table utilization and minimize no-shows

**Opportunities:**
- Automate the reservation process to reduce operational costs and staff workload
- Provide 24/7 availability for bookings, improving customer accessibility
- Leverage AI to personalize restaurant recommendations based on user preferences
- Collect valuable data on customer preferences and booking patterns

### Measurable Success Metrics & Potential ROI

**Key Metrics:**
- Reduction in staff time spent on reservation management (target: 70% reduction)
- Increase in online reservation rate vs. phone reservations (target: 40% increase)
- Customer satisfaction with the booking experience (target: 4.5/5 rating)
- System accuracy in understanding and executing reservation requests (target: 95%)
- Conversion rate from restaurant search to completed reservation (target: 30%)

**Potential ROI:**
- Labor cost savings: $X per restaurant per month
- Increased reservation volume: Y% increase in bookings
- Reduced no-show rate: Z% decrease through automated reminders
- Higher table utilization: Q% improvement in peak hours
- Cross-selling opportunities: R% increase in special event bookings

### Vertical Expansion Potential

The FoodieSpot platform could expand vertically into:

1. **Integrated Payments** - Allow users to pre-pay, leave deposits, or pay for meals through the platform
2. **Loyalty Programs** - Implement a points system to reward frequent diners
3. **Restaurant Management Tools** - Expand to include table management, waitlist handling, and staff scheduling
4. **Food Delivery Integration** - Connect with delivery services for restaurants that offer takeout
5. **Special Event Booking** - Facilitate private dining and special event reservations
6. **Customer Relationship Management** - Help restaurants maintain customer profiles and preferences

### Unique Competitive Advantages

- **AI-First Approach**: Using advanced LLM technology for natural language understanding creates a more intuitive user experience compared to form-based alternatives
- **Contextual Awareness**: The system maintains conversation history to provide personalized recommendations
- **Multi-Criteria Search**: Users can search based on various factors simultaneously (cuisine, location, party size, atmosphere)
- **Tool-Based Architecture**: The modular design allows for rapid addition of new features without redesigning the core system
- **Data Insights**: The platform can generate valuable insights for restaurants on customer preferences and booking patterns

## Example Conversations

### Example 1: Finding a Restaurant and Making a Reservation

**User**: "I'm looking for an Italian restaurant downtown for dinner tomorrow."

**Assistant**: "I can help you find Italian restaurants in the downtown area. Here are a few options:
1. Pasta Paradise - Authentic Italian cuisine with homemade pasta and wood-fired pizzas
2. Cafe Milano - Casual Italian cafe with espresso bar, pastries, and light fare
3. Bella Pizza - Neighborhood pizzeria with thin-crust pies and calzones

Would you like more details about any of these restaurants?"

**User**: "Tell me more about Pasta Paradise."

**Assistant**: "Pasta Paradise is located at 123 Main St in Downtown. They serve authentic Italian cuisine specializing in homemade pasta and wood-fired pizzas. They have a 4.5/5 rating and can accommodate up to 60 people. They're open from 11:00 to 22:00 Monday through Thursday, 11:00 to 23:00 on Friday and Saturday, and 12:00 to 21:00 on Sunday. The restaurant offers a romantic atmosphere, making it perfect for date nights. Would you like to check availability for a reservation?"

**User**: "Yes, I'd like to book a table for 4 people tomorrow at 7:30 PM."

**Assistant**: "I'll check availability at Pasta Paradise for 4 people tomorrow at 7:30 PM. What's the date tomorrow?"

**User**: "June 15, 2023"

**Assistant**: "Great! I've checked and Pasta Paradise has availability for 4 people on June 15, 2023 at 7:30 PM. Would you like me to make this reservation for you? If so, I'll need your name and contact phone number."

**User**: "Yes, please. My name is John Smith and my phone number is 555-123-4567."

**Assistant**: "Perfect! I've made your reservation at Pasta Paradise for 4 people on June 15, 2023 at 7:30 PM. Your confirmation code is RS-34567. They're located at 123 Main St in Downtown. Is there anything else you'd like help with?"

### Example 2: Handling Edge Cases

**User**: "I need a table for 20 people at Sushi Sensation tonight."

**Assistant**: "I'd be happy to check availability at Sushi Sensation for 20 people tonight. However, I should mention that Sushi Sensation has a seating capacity of 40 people, so a group of 20 would be a significant portion of their space. What time were you thinking of?"

**User**: "Around 8 PM"

**Assistant**: "I'm checking availability at Sushi Sensation for 20 people tonight at 8:00 PM. Unfortunately, they don't have availability for a group that size at that time. Their maximum party size for tonight is 15 people. Would you like me to suggest some alternative restaurants that might accommodate a group of 20 people? Or would you prefer to try a different date or time at Sushi Sensation?"

## Assumptions and Limitations

- **Data Simulation**: The current implementation simulates restaurant availability rather than connecting to a real-time reservation system
- **User Authentication**: The system doesn't include user accounts or authentication
- **Payment Processing**: No payment integration is included in this version
- **Limited Error Recovery**: While the system handles basic errors, complex error states might require human intervention
- **Availability Randomization**: For demonstration purposes, availability is randomized with an 80% chance of availability

## Future Enhancements

- **Real-time Availability**: Connect to a real restaurant management system for actual availability data
- **User Accounts**: Add user registration and login to save preferences and reservation history
- **Payment Integration**: Allow users to pay deposits or full amounts through the platform
- **Multi-modal Interaction**: Add support for image inputs (e.g., users could upload photos of cuisine types they like)
- **Group Reservation Coordination**: Facilitate group booking where multiple members can contribute to a reservation
- **Advanced Recommendations**: Implement a more sophisticated recommendation engine based on user history and preferences
- **Multilingual Support**: Add support for multiple languages to serve a more diverse user base
- **Integration with Maps**: Show restaurant locations on an interactive map 