import spacy
import random
from textblob import TextBlob
import requests
import re
import time
import logging
from fuzzywuzzy import fuzz

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('chatbot')

# Load spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Successfully loaded spaCy model")
except Exception as e:
    logger.error(f"Failed to load spaCy model: {e}")
    nlp = None

# Initialize session variables
session_data = {}

# Fetch company data with error handling and caching
company_data_cache = None
company_data_timestamp = 0
CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)

def get_company_data():
    global company_data_cache, company_data_timestamp

    # Return cached data if available and fresh
    current_time = time.time()
    if company_data_cache and current_time - company_data_timestamp < CACHE_DURATION:
        return company_data_cache

    try:
        response = requests.get('http://imancharlie.pythonanywhere.com/get_company_data', timeout=5)
        response.raise_for_status()
        company_data = response.json()
        # Update cache
        company_data_cache = company_data
        company_data_timestamp = current_time

        logger.info("Successfully fetched fresh company data")
        return company_data
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch company data: {e}")

        # Use cached data even if expired in case of failure
        if company_data_cache:
            logger.info("Using expired cached company data")
            return company_data_cache

        # Fallback data if no cache exists
        fallback_data = {
            "company_name": "Kodin Softwares",
            "industry": "software industry",
            "mission": "To provide websites and mobile applications that use advanced AI technology to tackle and provide solutions to improve businesses, institutions, organizations and individuals",
            "products": ["AI Chatbots", "Natural Language Processing", "Machine Learning Models", "Web Applications", "Mobile Applications"],
            "services": ["Custom AI Development", "AI Consulting", "Data Analytics", "Software Development", "Web Design", "Mobile App Development"],
            "contact_info": "kodinsoftwares@gmail.com",
            "phone": "+254 700 000000",
            "address": "Nairobi, Kenya",
            "website": "http://kodinsoftwares.pythonanywhere.com",
            "about": "At our core, we believe that #AnyoneCanCode and that nothing is impossible in software development. We are more than just a software company—we are a passionate collective driven by innovation and faith, serving a higher purpose of Almighty God through every line of code we create. Join us on this journey where technology meets divine inspiration, transforming challenges into groundbreaking opportunities."
        }

        # Update cache with fallback data
        company_data_cache = fallback_data
        company_data_timestamp = current_time

        logger.info("Using fallback company data")
        return fallback_data

# # Define response categories with multiple options for variety
responses = {
    "greeting": [
        "Hello! Welcome to {company_name}. How may I assist you today?",
        "Hi there! I'm delighted to welcome you to {company_name}. How can I help you?",
        "Greetings! Thanks for reaching out to {company_name}. What can I do for you today?",
        "Welcome to {company_name}! How may I be of service to you?",
        "Hello and welcome! How can I assist you with {company_name}'s services today?",
        "Hi! Thank you for contacting {company_name}. How can I help you today?",
        "Good day! Welcome to {company_name}. What brings you here today?",
        "Hello! It's a pleasure to welcome you to {company_name}. How may I assist you?"
    ],
    "name": [
        "I'm an AI assistant from {company_name}, designed to help with your inquiries.",
        "You can call me Kimi, your virtual assistant from {company_name}.",
        "I'm your digital concierge from {company_name}, here to assist with any questions.",
        "I'm the AI representative for {company_name}, ready to help with your needs.",
        "I'm Kimi, a virtual assistant powered by {company_name}'s AI technology.",
        "I'm a digital assistant from {company_name}, programmed to provide support and information.",
        "I'm an AI-powered helper from {company_name}, designed to assist customers like you."
    ],
    "mood": [
        "I'm functioning optimally and ready to assist you with any {company_name} related inquiries!",
        "I'm doing well, thank you for asking! How may I help you with {company_name}'s services today?",
        "I'm in excellent condition and eager to assist with your queries about {company_name}.",
        "I'm operational and ready to provide you with information about {company_name}. How can I help?",
        "I'm at your service and prepared to address any questions regarding {company_name}.",
        "I'm always ready to assist our valued customers. What can I help you with regarding {company_name}?"
    ],
    "bye": [
        "Goodbye! Thank you for connecting with {company_name}. We look forward to assisting you again soon.",
        "Farewell! It was a pleasure serving you. Feel free to reach out to {company_name} anytime.",
        "Thank you for chatting with {company_name}. Have a wonderful day ahead!",
        "It was a pleasure assisting you. {company_name} appreciates your interest. Goodbye!",
        "Thank you for your time. {company_name} is always here to help. Have a great day!",
        "Until next time! {company_name} values your connection. Goodbye!",
        "Thanks for chatting! Remember, {company_name} is just a message away whenever you need assistance."
    ],
    "joke": [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why don't scientists trust atoms? Because they make up everything!",
        "What's a computer's favorite snack? Microchips!",
        "Why did the developer go broke? Because they lost their domain!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "Why was the computer cold? It left its Windows open!",
        "What do you call a computer that sings? A Dell!"
    ],
    "small_talk": [
        "I'm here and ready to assist. How has your day been so far?",
        "Nothing much, just helping customers like you! How's your day going?",
        "I'm here to make your experience with {company_name} exceptional. How's your day treating you?",
        "Just assisting our valued clients at {company_name}. How about yourself?",
        "I'm focused on providing excellent service to you. How has your day been?"
    ],
    "company_info": [
        "{company_name} specializes in {industry}. Our mission is: {mission}",
        "Let me tell you about {company_name}. We are leaders in {industry} with a mission to {mission}",
        "{company_name} is dedicated to {mission} within the {industry}.",
        "As a key player in the {industry}, {company_name} is committed to {mission}.",
        "Our company, {company_name}, focuses on {mission} as part of our contribution to the {industry}."
    ],
    "products": [
        "{company_name} offers a range of products including: {products_list}",
        "Our product lineup at {company_name} includes: {products_list}",
        "At {company_name}, we've developed various products such as: {products_list}",
        "{company_name}'s product portfolio features: {products_list}",
        "We're proud to offer the following products at {company_name}: {products_list}"
    ],
    "services": [
        "{company_name} provides various services including: {services_list}",
        "Our service offerings at {company_name} include: {services_list}",
        "At {company_name}, we specialize in services such as: {services_list}",
        "{company_name}'s professional services encompass: {services_list}",
        "We offer a comprehensive range of services at {company_name}, including: {services_list}"
    ],
    "contact": [
        "You can contact {company_name} via email at {contact_info} or visit our website at {website}.",
        "For inquiries, please reach out to us at {contact_info} or check our website: {website}",
        "Feel free to contact us at {contact_info} or browse our website {website} for more information.",
        "To get in touch with {company_name}, email us at {contact_info} or visit {website}.",
        "Have questions? Contact us at {contact_info} or explore our website {website}."
    ],
    "website": [
        "You can explore our offerings at {website}. Would you like me to guide you through specific sections?",
        "Our website is available at {website}. It contains comprehensive information about our products and services.",
        "Visit us at {website} to learn more about {company_name} and what we offer.",
        "All the details about our company are available on our website: {website}",
        "For a complete overview of {company_name}, please visit {website}."
    ],
    "about": [
        "About {company_name}: {about}",
        "Here's what makes {company_name} special: {about}",
        "The essence of {company_name}: {about}",
        "Our story at {company_name}: {about}",
        "{company_name}'s core values and mission: {about}"
    ],
    "thank_you": [
        "You're welcome! It's my pleasure to assist you with {company_name}'s services.",
        "Happy to help! Is there anything else you'd like to know about {company_name}?",
        "It's my pleasure to be of service. {company_name} values your interest.",
        "You're most welcome! {company_name} is committed to providing excellent customer service.",
        "No problem at all! {company_name} appreciates your engagement."
    ],
    "pricing": [
        "Our pricing at {company_name} varies based on project specifications and requirements. Would you like to discuss a specific service for a customized quote?",
        "{company_name} offers tailored pricing solutions based on your needs. May I know which service you're interested in?",
        "At {company_name}, we provide custom quotes depending on project scope. Which service are you inquiring about?",
        "Our pricing structure at {company_name} is customized for each client. Would you like to schedule a consultation to discuss your specific needs?",
        "{company_name} offers competitive pricing in the {industry}. For detailed quotes, could you specify which service you're interested in?"
    ],
    "timeline": [
        "Project timelines at {company_name} depend on scope and complexity. Could you share more details about your project for a more accurate estimate?",
        "At {company_name}, we determine development timelines based on project requirements. What kind of project are you considering?",
        "The timeline for {company_name} projects varies based on specific needs. Could you tell me more about what you're looking to achieve?",
        "We pride ourselves on efficient delivery at {company_name}. To provide an estimated timeline, could you share some project details?",
        "{company_name} works diligently to meet project deadlines. For a specific timeline, I'd need to know more about your project scope."
    ],
    "portfolio": [
        "{company_name} has successfully completed numerous projects in the {industry}. Would you like to discuss specific case studies?",
        "Our portfolio at {company_name} showcases our expertise in {industry}. Are you interested in a particular type of project?",
        "{company_name} has an extensive track record of successful implementations. Which aspect of our work interests you most?",
        "We've delivered various solutions at {company_name} across different sectors. Would you like to hear about specific examples?",
        "{company_name}'s portfolio demonstrates our capability in delivering high-quality solutions. Which industry examples would you like to explore?"
    ],
    "capabilities": [
        "{company_name} specializes in {products_list} and offers services including {services_list}. Which capability interests you?",
        "Our technical expertise at {company_name} covers {products_list}. Is there a specific capability you'd like to explore?",
        "{company_name} has robust capabilities in developing {products_list}. Would you like more details on any specific area?",
        "At {company_name}, we excel in {services_list}. Which of these aligns with your needs?",
        "Our team at {company_name} is skilled in various technologies and methodologies for {products_list}. Is there a particular capability you're curious about?"
    ],
    "redirect": [
        "That's an interesting topic! While I'd love to explore that further, I'm specialized in providing information about {company_name} and our offerings in the {industry}. Is there something specific about our services I can help with?",
        "I appreciate your question! My primary focus is assisting with {company_name}'s services and products. How may I help you with your {industry} needs today?",
        "Thanks for sharing that! As {company_name}'s assistant, I'm here to help with your inquiries related to our offerings in {industry}. Is there something specific I can assist you with?",
        "That's a fascinating point! To best serve you, I'd like to focus on how {company_name} can meet your needs in the {industry}. What particular services are you interested in?",
        "I understand your interest in that topic. As {company_name}'s virtual assistant, I'm designed to provide information on our {industry} solutions. How can I help you with our services today?"
    ],
    "default": [
        "I'm not quite sure I understand. Could you please rephrase your question about {company_name} or our services?",
        "I apologize, but I didn't catch that. Could you please clarify what you'd like to know about {company_name}?",
        "I'm still learning and may have missed your point. Could you rephrase your question about our {industry} services?",
        "I want to provide the best assistance possible. Could you please restate your question about {company_name}?",
        "I apologize for any confusion. Could you please elaborate on your inquiry regarding {company_name}'s services?",
        "I'm sorry, but I'm not sure I fully understand your request. Could you provide more details about what you're looking for from {company_name}?"
    ],
    "careers": [
        "Thank you for your interest in {company_name}. Currently, we’re not hiring, but we’ll advertise new positions on {website} once they become available.",
        "We appreciate your enthusiasm about joining {company_name}. There are no openings right now, but please check {website} or call {support_phone} for future updates.",
        "At the moment, {company_name} has no active vacancies. Keep an eye on {website} or reach out via {support_phone} for any upcoming opportunities."
    ],
    "partnership": [
        "Yes, {company_name} is open to partnerships and collaborations! Feel free to visit {website} or call {support_phone} anytime for more details.",
        "We welcome collaboration at {company_name}. For partnership inquiries, please explore {website} or contact us at {support_phone}.",
        "Looking to partner with {company_name}? We’d love to discuss your ideas—visit {website} or dial {support_phone} for more info."
    ],
    "refund_policy": [
        "For refund-related concerns, please review our policy on {website} or email us at {contact_info}. We handle each case individually.",
        "We do our best to accommodate refund requests at {company_name}. Kindly check {website} for details or call {support_phone} to discuss your situation.",
        "Refunds are assessed on a case-by-case basis at {company_name}. Visit {website} or reach out via {contact_info} for assistance."
    ],
    "privacy_policy": [
        "We take privacy seriously at {company_name}. You can find our full policy on {website} or contact us at {contact_info} for more info.",
        "Your data security is a priority at {company_name}. Check {website} for our privacy policy or call {support_phone} if you have questions.",
        "At {company_name}, we respect user privacy. Please visit {website} to read our policy, or email {contact_info} for clarifications."
    ],
    "security": [
        "Security is paramount at {company_name}. We use robust encryption and conduct regular audits. Learn more on {website} or call {support_phone}.",
        "Rest assured, {company_name} employs industry-leading security measures to protect your data. For details, visit {website} or email {contact_info}.",
        "We prioritize cybersecurity at {company_name}—from SSL/TLS encryption to secure hosting. For specifics, see {website} or call {support_phone}."
    ],
    "testimonials": [
        "You can find client feedback and success stories on {website}. We appreciate all testimonials at {company_name}!",
        "Curious about what people say? Check out {website} for {company_name}’s testimonials, or call {support_phone} to share your own experience.",
        "We love hearing from satisfied customers. Visit {website} to read or submit testimonials for {company_name}."
    ],
    "support": [
        "For support or technical help, please email {contact_info} or call {support_phone}. {company_name} is here to assist you.",
        "Need assistance? {company_name} offers support through {contact_info} and phone at {support_phone}. We’ll be happy to help!",
        "Our support team is ready to assist. Contact {company_name} via {contact_info} or dial {support_phone} anytime."
    ],
    "maintenance": [
        "Yes, {company_name} provides ongoing maintenance and updates. Check {website} or call {support_phone} for details.",
        "We offer maintenance packages to keep your solutions running smoothly. Visit {website} or contact {support_phone} for more info.",
        "Ongoing support and maintenance are part of {company_name}’s services. Please reach out via {website} or {support_phone}."
    ]

}

# # Enhanced examples for better classification
# Enhanced examples for better classification
examples = {
    "greeting": [
        "hello", "hi", "hey", "hello there", "hey there", "hi there", "greetings", "good day",
        "good morning", "good afternoon", "good evening", "hiya", "howdy", "what's up", "hey what's up",
        "yo", "hey buddy", "hi buddy", "hello friend", "hey friend", "hi everyone", "hey everyone",
        "hey, how's it going", "hi, how are you", "morning", "afternoon", "evening", "hey, what's new",
        "hi, what's up", "hi friend", "hello again", "hey there, friend", "hey, what's happening",
        "hello, how are things", "hello folks", "hi folks", "hey folks", "what's good", "hi, nice to meet you",
        "pleasure to meet you"
    ],
    "name": [
        "what's your name", "who are you", "what do they call you", "who is this", "what's your name again",
        "can you tell me your name", "do you have a name", "what should I call you", "what's your name, please",
        "can you introduce yourself", "may I know your name", "introduce yourself", "what are you called",
        "your name is", "what name do you go by", "who am I talking to", "identify yourself", "what are you",
        "what's your identity", "tell me about yourself", "are you a bot", "are you an AI", "I want to know your name",
        "what do I call you", "please tell me your name", "what's the name you use", "who exactly are you",
        "tell me who you are", "what is your handle", "are you a chatbot", "are you a virtual assistant",
        "what's your official name", "who created you", "do you have a nickname", "are you Kimi",
        "tell me if you have a name", "could you say your name", "are you from Kodin Softwares",
        "which name do you prefer", "are you the Kodin Softwares bot"
    ],
    "mood": [
        "how are you", "how's your day", "how are you doing", "how do you feel", "how's it going", "what's up",
        "how are you today", "how's your day going", "how are you feeling", "how's your day been", "are you well",
        "feeling good", "how have you been", "how's everything", "how's life", "how are things", "are you doing well",
        "how's your mood", "are you okay", "you good", "you alright", "how's your system", "how are you, bot",
        "you in a good mood", "are you feeling fine", "are you in a good shape", "is everything okay with you",
        "are you having a good day", "what's your status", "are you feeling energetic", "are you feeling healthy",
        "are you having a good time", "how do you feel about working", "are you enjoying chatting", "do you have emotions",
        "are you happy", "how's your vibe", "are you bored", "are you busy", "what's your condition"
    ],
    "bye": [
        "goodbye", "see you later", "bye", "farewell", "catch you later", "see you soon", "goodbye for now",
        "see you", "bye-bye", "take care", "until next time", "later", "I'm leaving now", "have to go", "gotta go",
        "talk to you later", "catch you next time", "signing off", "I'll be going", "time to leave", "ending chat",
        "ending conversation", "see ya", "bye for now", "adios", "ciao", "I must go", "it was nice talking",
        "have a good day", "have a nice day", "I’m off", "I’m out", "peace out", "good night", "good evening",
        "take it easy", "be well", "so long", "closing the chat", "that's all for now"
    ],
    "joke": [
        "tell me a joke", "do you know any jokes", "make me laugh", "can you tell a joke", "I want to hear a joke",
        "tell me something funny", "do you have any jokes", "make me smile", "tell me a funny joke", "I need a laugh",
        "got any jokes", "say something funny", "humor me", "lighten the mood", "entertain me with a joke",
        "know any good jokes", "share a joke", "tell me a programming joke", "tell me a tech joke", "crack a joke",
        "make me chuckle", "I’m bored, tell me a joke", "any dad jokes", "any corny jokes", "any pun jokes",
        "funny stuff please", "hit me with a joke", "I could use a laugh", "any geeky jokes", "I love jokes, do you have any",
        "tell me something hilarious", "make me giggle", "any silly jokes", "any jokes about developers",
        "tell me a random joke", "I want a short joke", "give me a pun", "tell me a one-liner", "any riddles",
        "any witty jokes"
    ],
    "small_talk": [
        "what's up", "how's it going", "what are you doing", "what's new", "how's your day going", "what's happening",
        "what's going on", "how's your week", "what's the plan", "how's your evening", "what have you been up to",
        "anything new", "what's the latest", "what's happening today", "how's life treating you", "what's good",
        "how's business", "anything interesting", "got any news", "anything exciting", "what's up with you",
        "what's on your mind", "how's your day so far", "are you busy", "what's the gossip", "any updates",
        "how's your morning", "how's your afternoon", "how's your night", "tell me something new", "what's trending",
        "are you free", "just wanted to chat", "just checking in", "what's going on in your world", "anything fun happening",
        "what's the vibe", "how are things on your end", "how's everything going", "what's popping"
    ],
    "company_info": [
        "tell me about your company", "what does your company do", "what is your company", "who are you guys",
        "what's your business", "tell me about your business", "company information", "what is your company about",
        "what does your company specialize in", "tell me more about your organization", "company details",
        "what's your company history", "company overview", "what industry are you in", "what sector do you operate in",
        "what's your mission", "what's your company focus", "are you a startup", "tell me about Kodin Softwares",
        "describe your organization", "what's your corporate background", "how did your company start",
        "who founded your company", "when was your company established", "how big is your company",
        "where is your company located", "tell me your company's story", "what are your goals",
        "what's your main objective", "why did you start this company", "what sets your company apart",
        "do you have a mission statement", "how many employees do you have", "are you a global company",
        "who leads your company", "are you privately owned", "what is your company vision",
        "tell me about your corporate culture", "how long have you been in business", "what's your business model"
    ],
    "products": [
        "what products do you offer", "what do you sell", "show me your products", "what can I buy from you",
        "list your products", "product information", "what products do you have", "tell me about your products",
        "what solutions do you provide", "products overview", "what's your product line", "product details",
        "what can you build", "what software products do you have", "what technology products do you offer",
        "what kind of tools do you make", "do you have AI products", "do you offer any apps", "tell me your product range",
        "what do you develop", "are your products custom", "what existing products do you have",
        "where can I see your product list", "any examples of your products", "do you sell ready-made solutions",
        "are your products subscription-based", "can I get a demo of your products", "are your products open-source",
        "do you provide mobile apps", "do you have web-based products", "are your products for businesses or individuals",
        "do you offer any free tools", "what's your flagship product", "how many products do you have",
        "can you customize your products", "do you have a product catalog", "are your products scalable",
        "do you integrate AI into your products", "are your products cloud-based", "do you provide product documentation"
    ],
    "services": [
        "what services do you provide", "what do you do", "services offered", "what can you help me with",
        "list your services", "service information", "what services do you have", "tell me about your services",
        "how can you help me", "services overview", "what's your service catalog", "service details",
        "what solutions do you offer", "how do you help businesses", "what kind of work do you do",
        "do you offer consulting", "do you provide maintenance", "do you handle design", "do you do development",
        "do you do AI services", "are you a full-stack service", "do you do front-end or back-end",
        "do you handle cloud deployments", "what kind of integration services do you have", "do you offer training",
        "do you provide support", "what about testing services", "do you do data analytics", "can you build mobile apps",
        "can you develop websites", "do you offer project management", "do you do devops", "can you consult on AI",
        "what specialized services do you have", "how do you package your services", "do you do prototypes or MVPs",
        "do you do R&D", "can you do custom solutions", "do you do user experience design", "what's included in your service suite"
    ],
    "contact": [
        "how can I contact you", "contact information", "how do I reach you", "what's your contact info", "contact details",
        "how do I get in touch", "contact number", "email address", "what's your email", "phone number", "how to contact",
        "contact form", "where are you located", "office address", "headquarters location", "physical address",
        "where is your office", "how do I email you", "how do I call you", "do you have a hotline",
        "what's your official contact method", "can I chat with you", "do you have a live chat", "what's your fax number",
        "can I DM you", "are you on social media", "how do I send a message", "do you have a contact page",
        "who do I talk to for support", "do you have a support email", "is there a phone line for inquiries",
        "how do I submit a ticket", "do you have an office phone", "can I schedule a meeting", "do you have an online form",
        "where can I send my proposal", "any chat platform for contact", "do you have a WhatsApp line",
        "is there a personal contact for questions", "how do I request a callback"
    ],
    "website": [
        "what's your website", "do you have a website", "website link", "what's your URL", "company website",
        "where can I find your website", "online presence", "where can I find you online", "web address",
        "what's your domain", "website address", "can I see your website", "official website", "site URL",
        "show me your site", "do you have an official webpage", "where is your homepage", "what's your home URL",
        "how do I access your site", "send me your website link", "where can I browse your info",
        "where can I read more about you", "do you have an online portal", "where can I see your portfolio",
        "where is your product page", "can I see your blog", "what's your website about", "is your site live",
        "how do I get to your site", "do you have a landing page", "where can I see your services",
        "do you have an online store", "what's the link to your domain", "can I check your site now",
        "do you have a link to your site", "where is your official site", "is your site mobile-friendly",
        "can I find your contact info on your site", "is your website up to date", "do you have a web presence"
    ],
    "about": [
        "about your company", "company background", "tell me your story", "company history", "who you are",
        "company mission", "what's your company about", "company vision", "company values", "what do you stand for",
        "company culture", "company philosophy", "what's your purpose", "what's your mission", "company goals",
        "company objectives", "why do you exist", "how did you start", "where did you begin", "explain your background",
        "give me a summary of your company", "tell me the story behind your brand", "what's your origin",
        "why was this company created", "what drives your company", "what are your principles", "why should I trust you",
        "do you have a motto", "what's your reason for operating", "what's your guiding principle", "are you a faith-based company",
        "who leads the company direction", "why do you do what you do", "how did you come up with the idea",
        "what's your brand identity", "how did you form the team", "why do customers choose you", "what's your unique story",
        "do you have a big vision", "explain your company's DNA"
    ],
    "thank_you": [
        "thank you", "thanks", "thanks a lot", "thank you so much", "appreciate it", "thanks for your help",
        "thank you for the information", "thanks for the assistance", "many thanks", "thanks a bunch", "appreciate your help",
        "thank you kindly", "thanks for your time", "I appreciate it", "grateful for your help", "that's helpful, thanks",
        "you're a lifesaver", "I owe you one", "thanks for clarifying", "thank you, that was useful", "thank you, that helps a lot",
        "cheers for that", "much appreciated", "that was great, thanks", "thanks for the insight",
        "thank you for the explanation", "thanks, you're awesome", "thank you, I'm grateful", "I appreciate the details",
        "thank you, that's exactly what I needed", "you've been very helpful, thanks", "thank you for your patience",
        "I can't thank you enough", "you're very kind, thanks", "I truly appreciate your help",
        "that was incredibly helpful, thanks", "thank you for your quick response", "thanks for getting back to me",
        "I appreciate your thoroughness", "that's perfect, thank you"
    ],
    "pricing": [
        "how much does it cost", "what are your prices", "pricing information", "cost details", "how much do you charge",
        "what's your rate", "fee structure", "price list", "what's the cost", "how expensive is it", "what's the price range",
        "affordability", "budget considerations", "payment terms", "billing information", "quote request", "estimate request",
        "what's your pricing model", "pricing packages", "subscription cost", "how do you bill clients", "are your prices fixed",
        "do you charge hourly", "do you offer a free trial", "what is your minimum budget", "how flexible are your prices",
        "do you give discounts", "are there hidden fees", "do you have monthly plans", "what's your starting rate",
        "can I get a rough estimate", "how do you handle payment", "is there a deposit required", "do you do milestone payments",
        "are your rates negotiable", "do you have different tiers", "can you break down the costs", "do you charge by project scope",
        "is there a setup fee", "any additional charges"
    ],
    "timeline": [
        "how long does it take", "what's the timeline", "turnaround time", "development time", "project duration",
        "how quickly can you deliver", "completion timeframe", "estimated time", "delivery schedule", "project timeline",
        "implementation time", "how soon can you start", "development schedule", "production time", "how fast can you deliver",
        "typical project duration", "are you quick", "time to finish", "deadline", "timeframe", "can you do it urgently",
        "is there an express option", "when can I expect results", "time estimate", "how many weeks", "how many months",
        "how many days", "do you do agile", "do you have sprints", "can you do a short timeline", "when will it be done",
        "how do you schedule tasks", "what's your average delivery time", "can you meet tight deadlines", "how do you plan the project",
        "how do you handle project phases", "what's the maximum time", "can you do it in under a month",
        "can you do it in under a week", "how do you track progress"
    ],
    "portfolio": [
        "show me your work", "previous projects", "case studies", "client examples", "portfolio showcase",
        "past work", "success stories", "project examples", "work samples", "previous clients", "showcase projects",
        "sample work", "reference projects", "project gallery", "what have you built", "who have you worked with",
        "client testimonials", "project portfolio", "I want to see your demos", "do you have any references",
        "do you have any big clients", "what's your track record", "what's your best project", "where can I see your success stories",
        "do you have any examples of your solutions", "any highlight projects", "did you do any famous projects",
        "do you have a list of completed projects", "can I see your achievements", "any recognized work",
        "where is your portfolio page", "show me your completed apps", "did you build anything I know", "who are your partners",
        "how can I see your references", "did you work with any large companies", "any open-source projects you contributed to",
        "what industries have you served", "did you do any award-winning projects", "do you have a project showcase"
    ],
    "capabilities": [
        "what can you do", "technical capabilities", "technology stack", "expertise areas", "technical skills",
        "what technologies do you use", "development capabilities", "what languages do you code in", "technical proficiency",
        "skill set", "areas of expertise", "technical knowledge", "tech stack", "development platforms", "programming languages",
        "software expertise", "technical specialization", "how experienced are you", "do you do AI", "do you do machine learning",
        "do you do web dev", "do you do mobile dev", "are you good at data analytics", "can you do devops", "can you do cloud computing",
        "are you full-stack", "do you do front-end frameworks", "are you good at python", "do you use django", "do you handle big data",
        "can you do react", "do you do node.js", "do you do microservices", "do you do API integrations", "are you specialized in any frameworks",
        "do you handle AI chatbots", "do you do AR or VR", "how versatile are you", "do you do blockchain", "can you do cross-platform dev"
    ],
    "careers": [
        "are you hiring",
        "any job openings",
        "open positions",
        "job vacancies",
        "do you have internships",
        "career opportunities",
        "can I apply for a job",
        "how do I join your team",
        "looking for developers",
        "any software engineering roles",
        "what's your hiring process",
        "where can I submit my resume",
        "do you have remote jobs",
        "how do I see current vacancies",
        "do you offer graduate programs",
        "any part-time opportunities",
        "who do I contact about jobs",
        "how can I become an intern",
        "is there a career page on your site",
        "are you recruiting now",
        "do you need data scientists",
        "what roles are you looking to fill",
        "can I schedule an interview",
        "do you do campus hiring",
        "are you open to freelance workers"
    ],
    "partnership": [
        "do you do partnerships",
        "are you open to collaboration",
        "how can I partner with you",
        "strategic partnership inquiry",
        "I'd like to team up with your company",
        "can we form an alliance",
        "do you do joint ventures",
        "do you collaborate with startups",
        "looking for business partners",
        "how do I propose a partnership",
        "I want to discuss a collaboration",
        "do you accept reseller partners",
        "are you open to distribution partnerships",
        "can we co-brand a product",
        "who handles partnerships in your company",
        "any affiliate programs",
        "do you do technology partnerships",
        "looking for a channel partner deal",
        "can we do a revenue share model",
        "interested in co-marketing opportunities",
        "who can I talk to about alliances",
        "is there a partnership form on your website",
        "how do I pitch a partnership idea",
        "do you partner with NGOs or nonprofits",
        "are you interested in sponsor deals"
    ],
    "refund_policy": [
        "what is your refund policy",
        "can I get my money back",
        "do you offer refunds",
        "how do I request a refund",
        "money-back guarantee",
        "do you have a returns policy",
        "can I cancel and get a refund",
        "how long does it take to process a refund",
        "is there a time limit for refunds",
        "do you offer partial refunds",
        "who do I contact about a refund",
        "are refunds automatic",
        "any cancellation fees",
        "do you charge a restocking fee",
        "can I get a refund if I'm not satisfied",
        "do you offer a free trial with refund",
        "what if the project fails",
        "do you have a satisfaction guarantee",
        "can I dispute a charge",
        "how do I see your terms for refunds",
        "is there a cooling-off period",
        "do you issue credits instead of refunds",
        "do you provide store credit",
        "can I exchange services instead of refund",
        "any exceptions to your refund policy"
    ],
    "privacy_policy": [
        "what is your privacy policy",
        "how do you handle my data",
        "do you collect personal information",
        "where can I read your data policy",
        "how do you store user info",
        "do you share data with third parties",
        "can I opt out of data collection",
        "do you comply with GDPR",
        "how do you protect user privacy",
        "what data do you track",
        "is my information secure",
        "do you sell user data",
        "how do you handle cookies",
        "where can I find your privacy terms",
        "can I delete my data",
        "do you keep user logs",
        "is my info anonymous",
        "do you have a data retention policy",
        "who oversees privacy compliance",
        "can I request a data export",
        "how long do you keep personal data",
        "is your privacy policy publicly available",
        "how do I withdraw my consent",
        "what are your security measures",
        "can I contact a DPO or privacy officer"
    ],
    "security": [
        "is your platform secure",
        "what security measures do you have",
        "do you encrypt data",
        "are my transactions safe",
        "do you use SSL/TLS",
        "how do you protect against hacking",
        "are you ISO certified",
        "do you conduct penetration testing",
        "how do you handle data breaches",
        "do you have a bug bounty program",
        "is my password safe",
        "do you store credit card info",
        "are payments handled securely",
        "do you have multi-factor authentication",
        "do you have a dedicated security team",
        "how often do you update your security",
        "what’s your approach to cybersecurity",
        "is your API secure",
        "do you have security audits",
        "do you offer secure hosting",
        "are you compliant with industry standards",
        "do you use secure coding practices",
        "how do you handle user authentication",
        "what do you do if there’s a breach",
        "are your servers protected"
    ],
    "testimonials": [
        "do you have testimonials",
        "can I read customer reviews",
        "any feedback from your clients",
        "what do people say about you",
        "do you have success stories",
        "are there client references",
        "can I see some recommendations",
        "any endorsements on your site",
        "where can I find user reviews",
        "how do clients rate your services",
        "any big companies that endorse you",
        "do you have public case studies",
        "can I talk to a past client",
        "are there reviews on third-party sites",
        "do you showcase client feedback",
        "how do customers usually respond",
        "do you have a testimonial page",
        "can I see your ratings",
        "do you have star reviews",
        "how do you handle negative feedback",
        "are there quotes from satisfied clients",
        "do you have success metrics to share",
        "any awards or accolades",
        "how do I submit my testimonial",
        "do you post user success stories"
    ],
    "support": [
        "do you have customer support",
        "how do I get help",
        "can I open a support ticket",
        "who do I contact for issues",
        "what's your support process",
        "do you offer 24/7 support",
        "can I chat with support",
        "how do I reach technical assistance",
        "do you have phone support",
        "is there an email for help",
        "how do I escalate an issue",
        "can I get live support",
        "how fast is your response time",
        "do you offer emergency support",
        "where can I report bugs",
        "do you have a knowledge base",
        "can I track my support request",
        "do you offer paid support plans",
        "do you have a community forum",
        "can I schedule a support call",
        "what's your SLA for support",
        "how do you handle urgent requests",
        "can I contact your dev team directly",
        "is there a troubleshooting guide",
        "do you do remote support sessions"
    ],
    "maintenance": [
        "do you provide maintenance services",
        "how do you handle updates",
        "what's your maintenance plan",
        "do you offer post-launch support",
        "do you have ongoing maintenance packages",
        "how do you fix bugs after deployment",
        "is there a monthly retainer option",
        "do you handle software patches",
        "can you maintain my existing system",
        "how often do you roll out updates",
        "do you provide version upgrades",
        "can I subscribe to a maintenance contract",
        "how do you handle emergency fixes",
        "do you have a long-term support plan",
        "what if I need small changes",
        "do you do performance optimizations",
        "how do you schedule maintenance windows",
        "can you monitor uptime",
        "do you offer service continuity",
        "who do I call for maintenance requests",
        "is maintenance included in the initial price",
        "how do you handle major releases",
        "do you do site backups",
        "how do I report maintenance issues",
        "can you maintain third-party integrations"
    ]


}

# Precompute spaCy docs for examples
example_docs = {}
if nlp:
    for category in examples:
        example_docs[category] = [nlp(text) for text in examples[category]]

# FAQ database with common questions and answers
# FAQ database with common questions and answers
faqs = {
    "what technologies do you use": {
        "response": "At {company_name}, we utilize a variety of cutting-edge technologies including Python, Django, React, Node.js, TensorFlow, and other AI frameworks to deliver robust software solutions.",
        "category": "capabilities"
    },
    "how do i get started": {
        "response": "Getting started with {company_name} is easy! We begin with a consultation to understand your needs, then provide a proposal with timeline and pricing. Once approved, our development team starts working on your project with regular updates throughout the process.",
        "category": "default"
    },
    "can you build custom software": {
        "response": "Absolutely! {company_name} specializes in custom software development tailored to your specific business needs. We handle everything from design to deployment and ongoing maintenance.",
        "category": "capabilities"
    },
    "do you offer maintenance": {
        "response": "Yes, {company_name} provides comprehensive maintenance and support services for all our software solutions. We offer various support packages to ensure your applications run smoothly long after deployment.",
        "category": "services"
    },
    "what makes you different": {
        "response": "{company_name} stands out through our commitment to innovation, excellence, and customer satisfaction. We combine technical expertise with a deep understanding of business needs, creating solutions that truly transform operations.",
        "category": "about"
    },
    "what's your company mission": {
        "response": "Our mission at {company_name} is to empower businesses with cutting-edge technology solutions that drive growth and success. We strive to deliver exceptional software products and services that exceed client expectations.",
        "category": "about"
    },
    "how do i contact support": {
        "response": "You can reach our support team by emailing {contact_info} or calling our main line. We're here to help you with any issues or questions!",
        "category": "support"
    },
    "are you open to partnerships": {
        "response": "Yes, {company_name} welcomes partnership opportunities! Please visit our website at {website} or reach out via {contact_info} to discuss potential collaborations.",
        "category": "partnership"
    },
    "what is your refund policy": {
        "response": "We handle refunds on a case-by-case basis at {company_name}. Please check {website} for our detailed refund policy or contact us directly at {contact_info}.",
        "category": "refund_policy"
    },
    "how do you ensure data privacy": {
        "response": "At {company_name}, we take data privacy seriously. We comply with relevant regulations and employ robust security measures. You can read our full privacy policy on {website}.",
        "category": "privacy_policy"
    },
    "what is your typical project timeline": {
        "response": "Project timelines vary depending on scope and complexity. After discussing your requirements, {company_name} will provide an estimated schedule and keep you updated throughout the process.",
        "category": "timeline"
    },
    "do you offer devops or cloud services": {
        "response": "Yes! {company_name} provides DevOps consulting, CI/CD implementation, and cloud deployment services. We tailor solutions to meet your specific needs and infrastructure.",
        "category": "capabilities"
    },
    "how do you handle security": {
        "response": "{company_name} employs best practices like SSL encryption, secure coding, and regular audits to protect your data. For more details, please visit {website}.",
        "category": "security"
    },
    "do you provide training or workshops": {
        "response": "Absolutely! {company_name} can conduct training sessions or workshops to help your team get up to speed on new technologies, frameworks, or AI tools.",
        "category": "services"
    },
    "do you have any client references or testimonials": {
        "response": "We love to share success stories! You can find testimonials on {website}, or contact us to learn more about our past projects.",
        "category": "testimonials"
    },
    "how do you handle cancellations": {
        "response": "If you need to cancel a project, please contact {company_name} as soon as possible. We’ll review the work completed and discuss any applicable fees or refunds.",
        "category": "refund_policy"
    }

}

# Enhanced entity recognition for specific business terms
business_entities = {
    "software": "product",
    "website": "product",
    "mobile app": "product",
    "application": "product",
    "development": "service",
    "consulting": "service",
    "design": "service",
    "training": "service",
    "support": "service",
    "maintenance": "service",
    "AI": "technology",
    "artificial intelligence": "technology",
    "machine learning": "technology",
    "NLP": "technology",
    "natural language processing": "technology",
    "chatbot": "product",
    "blockchain": "technology",
    "cloud": "technology",
    "web app": "product",
    "mobile application": "product"
}

def get_session_id(user_id="default"):
    """Get or create a session for the user"""
    if user_id not in session_data:
        session_data[user_id] = {
            "conversation_history": [],
            "user_name": None,
            "last_interaction": time.time(),
            "interests": [],
            "sentiment_history": []
        }
    return user_id

def format_response(template, company_data):
    """Format response templates with company data"""
    # Format products and services lists if they're lists
    products_list = ", ".join(company_data["products"]) if isinstance(company_data["products"], list) else company_data["products"]
    services_list = ", ".join(company_data["services"]) if isinstance(company_data["services"], list) else company_data["services"]

    # Create a copy of company_data and add formatted lists
    data = company_data.copy()
    data["products_list"] = products_list
    data["services_list"] = services_list

    # Format the template with the data
    return template.format(**data)

def detect_entities(text):
    """Detect business-related entities in text"""
    entities = []
    if nlp:
        doc = nlp(text.lower())
        # Standard NER
        for ent in doc.ents:
            entities.append({"text": ent.text, "label": ent.label_})

        # Custom business entity detection
        for term, category in business_entities.items():
            if term.lower() in text.lower():
                entities.append({"text": term, "label": category})

    return entities

def check_for_faq(text):
    """Check if the input matches any FAQ"""
    best_match = None
    best_score = 0

    # Clean input text
    cleaned_text = text.lower().strip()

    # Check for exact matches first
    if cleaned_text in faqs:
        return faqs[cleaned_text]

    # Then check for fuzzy matches
    for question in faqs:
        score = fuzz.ratio(cleaned_text, question.lower())
        if score > 80 and score > best_score:  # 80% similarity threshold
            best_score = score
            best_match = faqs[question]

    return best_match

def analyze_sentiment(text):
    """Analyze sentiment of input text"""
    blob = TextBlob(text)
    return {
        "polarity": blob.sentiment.polarity,  # Range: -1 (negative) to 1 (positive)
        "subjectivity": blob.sentiment.subjectivity  # Range: 0 (objective) to 1 (subjective)
    }

def extract_user_interests(text, entities):
    """Extract potential user interests from text and entities"""
    interests = []

    # Extract from business entities
    for entity in entities:
        if entity["label"] in ["product", "service", "technology"]:
            interests.append(entity["text"])

    # Extract from keywords
    keywords = ["interested in", "looking for", "need", "want", "searching for", "seeking"]
    for keyword in keywords:
        if keyword in text.lower():
            # Extract the phrase after the keyword
            pattern = f"{keyword}(.*?)(\\.|\\?|,|$)"
            matches = re.findall(pattern, text.lower())
            if matches:
                for match in matches:
                    interests.append(match[0].strip())

    return list(set(interests))  # Remove duplicates

def classify_text(text, user_id="default"):
    """Classify user input into a category"""
    session = session_data.get(user_id, {
        "conversation_history": [],
        "user_name": None,
        "interests": []
    })

    # Check for FAQs first
    faq_match = check_for_faq(text)
    if faq_match:
        return {"category": faq_match["category"], "faq": True, "response": faq_match["response"]}

    # Clean and prepare the text
    cleaned_text = text.lower().strip()

    # Check for introduction patterns
    intro_patterns = [
        r"(?:my name is|i am|i'm|call me) (\w+)",
        r"(\w+) (?:here|speaking)"
    ]

    for pattern in intro_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            return {"category": "introduce", "name": match.group(1).capitalize()}

    # Detect entities
    entities = detect_entities(text)

    # Extract interests
    interests = extract_user_interests(text, entities)
    if interests:
        session["interests"].extend(interests)
        # Remove duplicates while preserving order
        session["interests"] = list(dict.fromkeys(session["interests"]))

    # Check for specific keywords
    for category, terms in examples.items():
        for term in terms:
            if term in cleaned_text or cleaned_text in term:
                return {"category": category}

    # If no direct match, use NLP similarity if spaCy is available
    if nlp:
        doc = nlp(cleaned_text)

        similarities = {}
        for category, docs in example_docs.items():
            if docs:  # Ensure the category has example documents
                sims = [doc.similarity(d) for d in docs]
                similarities[category] = max(sims) if sims else 0

        if similarities:
            max_category = max(similarities, key=similarities.get)
            if similarities[max_category] > 0.5:  # Threshold for confidence
                return {"category": max_category}

    # Context-aware classification based on conversation history
    if session["conversation_history"]:
        last_category = session["conversation_history"][-1].get("category")

        # Check if follow-up to a specific category
        followup_patterns = {
            "products": ["which ones", "what are they", "tell me more", "features", "benefits"],
            "services": ["what services", "tell me more", "how do you", "can you help"],
            "pricing": ["how much", "cost", "price", "expensive", "cheap", "affordable"],
            "timeline": ["how long", "when", "time", "schedule", "deadline", "deliver"]
        }

        for category, patterns in followup_patterns.items():
            if any(pattern in cleaned_text for pattern in patterns):
                if last_category == category or last_category in ["default", "redirect"]:
                    return {"category": category}

    # Default if all else fails
    for entity in entities:
        if entity["label"] == "product":
            return {"category": "products"}
        elif entity["label"] == "service":
            return {"category": "services"}

    return {"category": "default"}
def personalize_response(response, user_id="default"):
    """Personalize response based on user data"""
    session = session_data.get(user_id, {
        "user_name": None,
        "interests": []
    })

    company_data = get_company_data()
    response = format_response(response, company_data)

    # Add name personalization if available
    if session["user_name"] and random.random() < 0.7:  # 70% chance to use name
        if not response.startswith(session["user_name"]):
            response = f"{session['user_name']}, {response.lower()}"

    # Add interests personalization if available
    if session["interests"]:
        interests_str = ", ".join(session["interests"])
        response += f"\n\nBased on your interests in {interests_str}, how can I assist you further?"

    return response

def chatbot_response(user_input, user_id="default"):
    """Generate a response based on user input"""
    user_id = get_session_id(user_id)
    session = session_data[user_id]

    # Classify the input
    result = classify_text(user_input, user_id)
    category = result["category"]

    # Handle introduction and store user name
    if category == "introduce":
        session["user_name"] = result["name"]
        session["conversation_history"].append({"category": "introduce", "name": session["user_name"]})
        return f"Nice to meet you, {session['user_name']}!"

    # Handle FAQ responses
    if "faq" in result:
        session["conversation_history"].append({"category": category, "faq": True})
        return personalize_response(result["response"], user_id)

    # Handle sentiment analysis
    sentiment = analyze_sentiment(user_input)
    if sentiment["polarity"] < -0.5:
        response = "I'm sorry to hear that you're feeling down. Is there anything I can do to help?"
    elif sentiment["polarity"] > 0.5:
        response = "That's great to hear! I'm glad you're feeling positive."
    else:
        # Standard response with personalization if name is known
        response = random.choice(responses[category])

    # Personalize the response
    response = personalize_response(response, user_id)

    # Update conversation history
    session["conversation_history"].append({"category": category})

    return response

# Example usage
if __name__ == "__main__":
    user_id = "user123"
    print(chatbot_response("My name is Alice", user_id))  # "Nice to meet you, Alice!"
    print(chatbot_response("How are you?", user_id))     # "Alice, i'm just a bot, but i'm doing great!"
    print(chatbot_response("What's the weather like?", user_id))  # "Alice, i don't have real-time weather data..."
    print(chatbot_response("What about tomorrow?", user_id))  # "I don't have weather forecasts, but I hope... "
    print(chatbot_response("I'm feeling sad", user_id))  # "I'm sorry to hear that you're feeling down..."
    print(chatbot_response("Tell me a joke", user_id))  # "Alice, i'd love to chat about that another time, but let's focus on your business needs. what can i assist you with today?"
    print(chatbot_response("I need business advice", user_id))  # "Sure, I'd be happy to help with that. What specific aspects of business are you looking for information on?"

