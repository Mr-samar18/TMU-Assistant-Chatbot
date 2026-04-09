
from flask import Flask, render_template, request, jsonify
from rapidfuzz import fuzz, process
from datetime import datetime
import re


app = Flask(__name__)



THRESHOLD = 55  


def clean_text(text):
    """
    Normalize user input for better matching
    """
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", "", text)   
    text = re.sub(r"\s+", " ", text)      
    return text


def fallback_answer():
    return (
        "I'm not sure about that yet, but I can help you with:\n\n"
        "- TMU overview\n"
        "- Courses and programs\n"
        "- BCA, B.Tech, MBA, BBA, B.Com, MCA, M.Tech, Law, Pharmacy, Nursing and more\n"
        "- Fees and eligibility\n"
        "- Hostel and facilities\n"
        "- Placements\n"
        "- Admission process\n"
        "- Scholarships\n"
        "- Contact and campus details\n\n"
        "You can also visit the official TMU website:\n"
        "https://www.tmu.ac.in\n\n"
        "Try asking something like:\n"
        "- What courses are offered in TMU?\n"
        "- What is the fee for B.Tech?\n"
        "- Does TMU provide hostel?\n"
        "- What is the eligibility for MBA?"
    )

qa_pairs = {

    # ---------------- GREETINGS ----------------
    "hi": "Hello! How can I help you?",
    "hello": "Hello! How can I help you?",
    "hey": "Hey! Ask me anything about TMU.",
    "hlo": "Hi there! How can I assist you today?",
    "good morning": "Good morning! How can I help you with TMU information?",
    "good evening": "Good evening! Ask me anything about TMU.",

    # ---------------- GENERAL TMU INFO ----------------
    "tell me about tmu": (
        "Teerthanker Mahaveer University (TMU) is a private university located in Moradabad, "
        "Uttar Pradesh. It was established in 2008 and is known for offering a wide range of "
        "programs in engineering, management, medical sciences, law, pharmacy, nursing, "
        "computer applications, and more."
    ),

    "what is tmu": (
        "TMU stands for Teerthanker Mahaveer University. It is a private university in Moradabad, "
        "Uttar Pradesh, offering undergraduate, postgraduate, diploma, and doctoral programs."
    ),

    "full form of tmu": "TMU stands for Teerthanker Mahaveer University.",

    "where is tmu located": "TMU is located in Moradabad, Uttar Pradesh, India.",

    "tmu location": "TMU is located in Moradabad, Uttar Pradesh, India.",

    "is tmu ugc approved": "Yes, TMU is recognized by the University Grants Commission (UGC).",

    "is tmu naac accredited": "Yes, TMU is accredited by NAAC.",

    "is tmu private or government": "TMU is a private university.",

    "when was tmu established": "TMU was established in 2008.",

    "official website of tmu": "The official website of TMU is: https://www.tmu.ac.in",

    "tmu official website": "The official website of TMU is: https://www.tmu.ac.in",

    "how to contact tmu": "You can contact TMU through their official contact page: https://www.tmu.ac.in/contact-us",

    "contact number of tmu": "You can find TMU contact details here: https://www.tmu.ac.in/contact-us",

    "email of tmu": "You can find official TMU contact email details here: https://www.tmu.ac.in/contact-us",

    # ---------------- COURSES GENERAL ----------------
    "what courses are offered in tmu": (
        "TMU offers a wide range of courses in:\n"
        "- Engineering & Technology\n"
        "- Computer Applications\n"
        "- Management\n"
        "- Commerce\n"
        "- Law\n"
        "- Medical & Dental Sciences\n"
        "- Pharmacy\n"
        "- Nursing\n"
        "- Agriculture\n"
        "- Paramedical Sciences\n"
        "- Education\n"
        "- Fine Arts\n"
        "- Journalism & Mass Communication\n\n"
        "Visit: https://www.tmu.ac.in/courses"
    ),

    "courses in tmu": (
        "TMU offers UG, PG, Diploma, and Doctoral programs in engineering, management, law, "
        "pharmacy, nursing, computer applications, commerce, medical sciences, and more.\n\n"
        "Visit: https://www.tmu.ac.in/courses"
    ),

    "programs offered by tmu": (
        "TMU offers undergraduate, postgraduate, diploma, and PhD programs in multiple fields "
        "such as engineering, management, law, computer applications, pharmacy, nursing, "
        "commerce, agriculture, and medical sciences."
    ),

    # ---------------- BCA ----------------
    "what is bca": (
        "BCA stands for Bachelor of Computer Applications — a 3-year undergraduate program "
        "focused on computer science, programming, and software development."
    ),

    "bca course in tmu": (
        "TMU offers BCA and BCA (Hons with Research) under the Faculty of Computing Sciences & IT. "
        "The course covers programming, web development, databases, AI, and software engineering."
    ),

    "tell me about bca in tmu": (
        "BCA at TMU is a 3-year (6-semester) program covering Python, C, C++, Java, DBMS, "
        "Operating Systems, Web Technologies, Data Structures, and AI fundamentals."
    ),

    "bca eligibility": (
        "Eligibility for BCA at TMU: 10+2 in any stream with at least 45–50% marks. "
        "Mathematics or Computer Science is preferred."
    ),

    "bca fees in tmu": (
        "The BCA course fee at TMU is approximately ₹30,500 per semester. "
        "For updated details, visit https://www.tmu.ac.in/admissions"
    ),

    "bca syllabus in tmu": (
        "The BCA syllabus includes:\n"
        "- Programming (C, C++, Python, Java)\n"
        "- DBMS\n"
        "- Web Development\n"
        "- Data Structures\n"
        "- Operating Systems\n"
        "- Computer Networks\n"
        "- Software Engineering\n"
        "- AI & Cloud basics"
    ),

    "career after bca": (
        "After BCA, students can work as Software Developers, Web Developers, "
        "Data Analysts, System Engineers, or pursue MCA, M.Sc, or MBA."
    ),

    # ---------------- MCA ----------------
    "what is mca": "MCA stands for Master of Computer Applications. It is a postgraduate course focused on advanced computer applications and software development.",

    "mca course in tmu": (
        "TMU offers MCA for students who want advanced knowledge in software development, "
        "programming, databases, networking, and application development."
    ),

    "mca eligibility": (
        "Eligibility for MCA generally includes a bachelor's degree with Mathematics at 10+2 or graduation level. "
        "Please check the latest details on TMU admissions page."
    ),

    "mca fees in tmu": (
        "For updated MCA fee details, please visit TMU admissions page:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    # ---------------- BTECH ----------------
    "btech course in tmu": (
        "TMU offers B.Tech programs in various specializations such as Computer Science, "
        "Mechanical, Civil, Electrical, AI & ML, and Data Science."
    ),

    "btech in tmu": (
        "TMU offers B.Tech in multiple engineering branches including CSE, Mechanical, Civil, "
        "Electrical, AI & ML, and Data Science."
    ),

    "engineering courses in tmu": (
        "TMU offers B.Tech, M.Tech, and PhD programs in engineering fields like CSE, "
        "Mechanical, Civil, Electrical, AI & ML, and Data Science."
    ),

    "btech eligibility": (
        "Eligibility for B.Tech at TMU generally requires 10+2 with Physics, Chemistry, and Mathematics."
    ),

    "btech fees in tmu": (
        "For updated B.Tech fee details, visit:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    "btech branches in tmu": (
        "TMU offers B.Tech branches such as:\n"
        "- Computer Science Engineering\n"
        "- Mechanical Engineering\n"
        "- Civil Engineering\n"
        "- Electrical Engineering\n"
        "- AI & ML\n"
        "- Data Science"
    ),

    # ---------------- MTECH ----------------
    "mtech course in tmu": (
        "TMU offers M.Tech programs for students who want advanced technical specialization in engineering."
    ),

    "mtech eligibility": (
        "Eligibility for M.Tech generally requires a B.Tech or equivalent engineering degree."
    ),

    "mtech fees in tmu": (
        "For updated M.Tech fee details, visit:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    # ---------------- BBA ----------------
    "what is bba": "BBA stands for Bachelor of Business Administration. It is a 3-year undergraduate management program.",

    "bba course in tmu": (
        "TMU offers BBA for students interested in business, management, marketing, finance, "
        "human resources, and entrepreneurship."
    ),

    "bba eligibility": (
        "Eligibility for BBA at TMU is generally 10+2 in any stream."
    ),

    "bba fees in tmu": (
        "For updated BBA fee details, visit:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    "career after bba": (
        "After BBA, students can work in management, marketing, sales, HR, operations, or pursue MBA."
    ),

    # ---------------- MBA ----------------
    "what is mba": "MBA stands for Master of Business Administration. It is a postgraduate program focused on business and management.",

    "mba course in tmu": (
        "TMU offers MBA programs for students who want to build careers in management, finance, "
        "marketing, HR, operations, and business leadership."
    ),

    "mba eligibility": (
        "Eligibility for MBA generally requires a bachelor's degree from a recognized university."
    ),

    "mba fees in tmu": (
        "For updated MBA fee details, visit:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    "career after mba": (
        "After MBA, students can work as Managers, Business Analysts, Marketing Executives, HR Managers, "
        "Finance Professionals, or Entrepreneurs."
    ),

    # ---------------- BCOM / MCOM ----------------
    "bcom course in tmu": (
        "TMU offers B.Com for students interested in accounting, finance, taxation, banking, "
        "and business studies."
    ),

    "bcom eligibility": "Eligibility for B.Com is generally 10+2 in any stream, preferably commerce.",

    "bcom fees in tmu": (
        "For updated B.Com fee details, visit:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    "mcom course in tmu": (
        "TMU offers M.Com for advanced studies in commerce, finance, accounting, and business."
    ),

    "mcom eligibility": "Eligibility for M.Com generally requires a B.Com or equivalent degree.",

    # ---------------- LAW ----------------
    "law course in tmu": (
        "TMU offers law programs such as BA LLB, BBA LLB, and LLB for students interested in legal education."
    ),

    "ba llb in tmu": (
        "TMU offers BA LLB as an integrated law program combining humanities and legal studies."
    ),

    "bba llb in tmu": (
        "TMU offers BBA LLB for students who want knowledge of both business and law."
    ),

    "llb in tmu": (
        "TMU offers LLB for students who want to build a career in the legal field."
    ),

    "law eligibility in tmu": (
        "Eligibility for law courses depends on the specific program such as BA LLB, BBA LLB, or LLB. "
        "Please check the official admissions page for latest details."
    ),

    # ---------------- PHARMACY ----------------
    "pharmacy course in tmu": (
        "TMU offers pharmacy courses such as D.Pharm, B.Pharm, M.Pharm, and related programs."
    ),

    "bpharm in tmu": (
        "TMU offers B.Pharm for students interested in medicines, pharmaceutical sciences, and healthcare."
    ),

    "dpharm in tmu": (
        "TMU offers D.Pharm for students who want to enter the pharmacy profession."
    ),

    "pharmacy eligibility": (
        "Eligibility for pharmacy courses generally depends on PCM/PCB in 10+2 for undergraduate programs."
    ),

    # ---------------- NURSING ----------------
    "nursing course in tmu": (
        "TMU offers nursing programs such as B.Sc Nursing, GNM, ANM, and postgraduate nursing courses."
    ),

    "bsc nursing in tmu": (
        "TMU offers B.Sc Nursing for students interested in healthcare, patient care, and hospital services."
    ),

    "gnm in tmu": "TMU offers GNM nursing program for students interested in nursing and patient care.",

    "anm in tmu": "TMU offers ANM nursing program as an entry-level nursing and healthcare course.",

    "nursing eligibility": (
        "Eligibility for nursing courses generally depends on the specific course and required subjects in 10+2."
    ),

    # ---------------- MEDICAL / PARAMEDICAL ----------------
    "medical courses in tmu": (
        "TMU offers medical, dental, paramedical, and allied health science programs through its health science faculties."
    ),

    "paramedical courses in tmu": (
        "TMU offers paramedical and allied health science programs for students interested in healthcare support fields."
    ),

    "dental courses in tmu": (
        "TMU also offers dental education programs through its dental college."
    ),

    # ---------------- AGRICULTURE ----------------
    "agriculture courses in tmu": (
        "TMU offers agriculture-related programs for students interested in agricultural sciences and related fields."
    ),

    "bsc agriculture in tmu": (
        "TMU offers B.Sc Agriculture for students interested in crop science, soil science, agronomy, and agriculture technology."
    ),

    # ---------------- ADMISSION ----------------
    "admission process in tmu": (
        "To take admission in TMU, students generally need to:\n"
        "- Choose a course\n"
        "- Check eligibility\n"
        "- Fill out the application form\n"
        "- Submit required documents\n"
        "- Complete fee/payment process\n\n"
        "Visit: https://www.tmu.ac.in/admissions"
    ),

    "how to get admission in tmu": (
        "You can apply for admission through TMU's official admissions page:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    "how to apply in tmu": (
        "You can apply online through TMU admissions portal:\n"
        "https://www.tmu.ac.in/admissions"
    ),

    "documents required for admission in tmu": (
        "Documents generally required include:\n"
        "- 10th marksheet\n"
        "- 12th marksheet\n"
        "- Graduation marksheets (for PG courses)\n"
        "- ID proof\n"
        "- Passport size photos\n"
        "- Transfer/Migration certificate (if applicable)\n"
        "- Category certificate (if applicable)"
    ),

    # ---------------- FEES / SCHOLARSHIP ----------------
    "fee structure of tmu": (
        "TMU fee structure depends on the course and program. "
        "For updated details, visit:\nhttps://www.tmu.ac.in/admissions"
    ),

    "scholarship in tmu": (
        "TMU may provide scholarships or financial assistance depending on eligibility and merit. "
        "Please check the official admissions page for updated details."
    ),

    "does tmu provide scholarship": (
        "TMU may offer scholarship opportunities depending on merit, eligibility, or university policy."
    ),

    # ---------------- HOSTEL / CAMPUS ----------------
    "does tmu have hostel facilities":
        "Yes, TMU provides separate hostels for boys and girls with Wi-Fi, mess, and security.",

    "hostel in tmu":
        "Yes, TMU provides hostel facilities for students with basic amenities like accommodation, food, and security.",

    "hostel fees in tmu":
        "For updated hostel fee details, please check the official TMU website or contact admissions.",

    "campus facilities in tmu": (
        "TMU campus facilities include:\n"
        "- Hostels\n"
        "- Library\n"
        "- Labs\n"
        "- Wi-Fi\n"
        "- Sports facilities\n"
        "- Cafeteria\n"
        "- Transport\n"
        "- Medical support"
    ),

    "does tmu have library":
        "Yes, TMU has library facilities for students.",

    "does tmu have wifi":
        "Yes, TMU provides campus facilities including Wi-Fi in many areas.",

    "does tmu have transport":
        "TMU may provide transport facilities for students. Please check with the university for updated route details.",

    # ---------------- PLACEMENTS ----------------
    "does tmu have placement opportunities":
        "Yes, TMU has a dedicated Training & Placement Cell with companies like TCS, Infosys, Wipro, and HCL.",

    "placements in tmu": (
        "TMU has a Training & Placement Cell that helps students with placement opportunities, "
        "career guidance, and company recruitment drives."
    ),

    "companies visiting tmu": (
        "Companies such as TCS, Infosys, Wipro, and HCL have been associated with placement opportunities at TMU."
    ),

    "highest package in tmu": (
        "For the latest and official placement statistics, please check TMU's official website or placement page."
    ),

    # ---------------- STUDENT LIFE ----------------
    "campus life in tmu": (
        "TMU offers a vibrant campus life with academics, events, cultural activities, sports, and student facilities."
    ),

    "events in tmu": (
        "TMU organizes academic, cultural, sports, and student engagement events throughout the year."
    ),

    "is tmu good for students": (
        "TMU offers multiple courses, campus facilities, hostel, and placement support, making it a good option for many students depending on their goals."
    ),

    # ---------------- BOT ----------------
    "who created you": "I was created as part of a college academic project using Python and Flask.",
    "what can you do": (
        "I can help you with TMU-related information such as courses, fees, eligibility, admissions, hostel, placements, scholarships, and campus details."
    ),

    "thanks": "You're welcome!",
    "thank you": "Happy to help!",
    "bye": "Goodbye! Have a great day!"
}

@app.route("/")
def home():
    """
    Render main chatbot UI
    """
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    """
    Handle chatbot questions
    """
    data = request.get_json(silent=True) or {}
    user_question = data.get("question", "")

    
    cleaned = clean_text(user_question)

    timestamp = datetime.now().strftime("%H:%M")

    
    if not cleaned:
        return jsonify({
            "answer": "Please type a question.",
            "timestamp": timestamp
        })

    
    if len(cleaned.split()) == 1 and cleaned not in [
    "bca", "mca", "btech", "mba", "bba", "bcom", "law",
    "hostel", "placements", "admission", "fees", "courses",
    "nursing", "pharmacy", "agriculture", "tmu"
]:
        return jsonify({
        "answer": (
            "Please ask a complete question, for example:\n"
            "- BCA fees in TMU\n"
            "- Does TMU have hostel facilities?\n"
            "- What courses are offered in TMU?"
        ),
        "timestamp": timestamp
    })

    
    questions = list(qa_pairs.keys())
    match = process.extractOne(cleaned, questions, scorer=fuzz.token_sort_ratio)

    if match:
        best_match, score, _ = match

        if score >= THRESHOLD:
            answer = qa_pairs[best_match]
        else:
            answer = fallback_answer()
    else:
        answer = fallback_answer()

    return jsonify({
        "answer": answer,
        "timestamp": timestamp
    })


if __name__ == "__main__":
    app.run(debug=True)
