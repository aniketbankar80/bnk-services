# BNK Services Website Development

This project focuses on building a comprehensive website for BNK Services with distinct modules for members and admins. The site will feature a modern, responsive design with mobile-first principles and a modular architecture that allows each feature to be developed independently. Ensure to integrate token-based authentication in all critical areas.

---

## Technology Stack

- **Frontend & Backend:**
			-	Python with Django (incorporating Django Jazzmin for an enhanced admin interface)
			- 	Modern design with mobile responsiveness, featuring a navigation bar that adapts to both desktop and mobile devices (hamburger menu for mobile view)
- **Architecture:** Modular design to facilitate independent development of features

---

## For Members

### Key Features

1. **Welcome Screen and Navigation**
   - **Welcome Page:** Develop a visually appealing welcome screen that displays immediately when the site loads.
   - **Navigation Bar:** Build a responsive navigation bar optimized for both desktop and mobile. Make sure to add content on pages.

2. **Member Authentication**
   - **Login/Logout:** Implement a simple yet secure login and logout system exclusively for members.
   - **Important Details:** 
     - Member ID and password are managed via the admin panel (new registrations or password resets are not needed).
     - gmail verification is not required for now.

3. **Loan Application Form**
   - **Application Process:** Members will have the capability to fill out a loan application form and also view their submitted applications.
   - **Editable Form:** The form must support actions like editing, updating, and deleting applications that are either pending or rejected.
   - **Form Fields Include:**
     - **Personal Information:**
       - Full Name
       - Date of Birth
       - Contact Number
       - Email Address
       - PAN Card Number (or SSN/National ID)
       - Aadhar Number
       - Residential Address
     - **Employment & Income Details:**
       - Income Source
       - Monthly Income
     - **Loan Details:**
       - Loan Type – provide a dropdown menu with options:
         - Personal Loan
         - Business Loan
         - Mortgage Loan
         - Salaried Loan
         - Vehicle Loan
         - Other Loan
       - Loan Amount Required
       - Loan Tenure
       - Purpose of Loan
     - **Additional Information:**
       - DSA Code / Register Mobile Number
       - Document Uploads
       - Declaration & Agreement (with a checkbox for Terms & Conditions acceptance)

4. **Member Payout Form**
   - Develop a separate payout form for members to receive their commission. The form should include:
     - DSA Code / Registered Mobile Number
     - Application Number
     - Customer Full Name
     - Customer Mobile Number
     - Bank/NBFC/Credit Card Name
     - Disburse Amount
     - Location
     - Disburse Date
     - Customer PAN Card
     - Upload option (for Pan card, application or email screenshot)

5. **Post-Login Navigation Bar**
   - Once logged in, members should see a navigation bar with the following pages:
     - Home
     - Apply for Loan
     - Status
     - Payout Form
     - DSA code list

---

## For Admins

### Key Features

1. **Admin Authentication**
   - **Login/Logout:** Build a secure login/logout system specifically for admin users.

2. **Admin Dashboard**
   - **Overview:** Create an intuitive admin panel that provides an overview of site data.
   - **Data Management:** 
     - Enable viewing, filtering, and deleting of data submitted by members.
     - Provide a dedicated section for direct customer inquiries.
   - **Loan Status Management:** Allow admins to update loan statuses (e.g., Approved, Rejected, Pending, Verified, Incomplete Documents, Disbursed).
   - **Data Export/Import:** Provide options for downloading member and customer data in CSV format.
   - **Form Builder:** Implement a dynamic form builder to add, modify, or remove fields from the loan application form.
   - **Member Management:** 
     - Build features to create, update, and delete member accounts, including fields such as Name, Mobile Number, Role, User ID, Email ID, Password, and Confirm Password.
     - Integrate role-based authentication with roles like Admin, Member, and User.
     - Enable import/export of member data via CSV.

3. **Storage and Database Configuration**
   - **Database Setup:** Include configuration options for setting up and managing the local database.
   - **Storage Options:** 
     - Allow configuration for either local storage or integration with AWS S3 for document storage.
     - Organize documents efficiently (e.g., categorizing files in folders named after each customer).
   - **User-Friendly Settings:** Ensure the configuration interface is intuitive enough for non-technical users.

4. **About & Privacy Information**
   - **About App:** Provide a section that explains the purpose of the application (i.e., managing bank-related loan applications).
   - **Privacy Policy:** Clearly outline the privacy policy regarding customer data and usage of the application.

---

## Development Plan

Before starting the coding phase, develop a comprehensive end-to-end development plan that outlines with adding detail on plan file:
- The overall project structure
- How each module functions independently
- Step-by-step guidelines to ensure seamless collaboration among team members