\# Secure Notes API (AWS – API Gateway, Lambda, DynamoDB, Cognito)



This project is a simple \*\*secure notes API\*\* built on AWS:



\- \*\*Amazon API Gateway (HTTP API)\*\* – public HTTPS endpoint

\- \*\*AWS Lambda\*\* – Python function with CRUD logic

\- \*\*Amazon DynamoDB\*\* – `Notes` table for storage

\- \*\*Amazon Cognito User Pool\*\* – user sign-up/sign-in and JWT access tokens

\- \*\*Static HTML tester\*\* – `notes.html` to exercise the API in the browser



Each user can only see and modify \*\*their own\*\* notes. Ownership is enforced in Lambda using the Cognito user’s `sub` claim.



---



\## 1. Architecture



\*\*Flow:\*\*



1\. User signs in via \*\*Cognito Hosted UI\*\* and gets an \*\*access token (JWT)\*\*.

2\. Frontend (`notes.html` or curl) calls the API Gateway endpoint:



&nbsp;  `https://ss5k5py93l.execute-api.ap-southeast-2.amazonaws.com/prod/notes`



&nbsp;  with header:



&nbsp;  `Authorization: Bearer <ACCESS\_TOKEN>`



3\. API Gateway:

&nbsp;  - Runs \*\*JWT authorizer\*\* against the Cognito user pool

&nbsp;  - On success, forwards the request (and JWT claims) to Lambda



4\. Lambda:

&nbsp;  - Reads user id from JWT: `event.requestContext.authorizer.jwt.claims.sub`

&nbsp;  - Performs CRUD operations in DynamoDB `Notes` table

&nbsp;  - Ensures the `owner` field matches the current user before returning/updating/deleting



---



\## 2. Repository layout



```text

notes-api/

├─ lambda\_function.py        # Lambda handler (Python)

├─ notes.html                # Browser-based API tester

├─ aws\_notes\_api\_cheatsheet.txt  # Optional CLI / curl cheatsheet

└─ README.md                 # This file

3\. Lambda details



File: lambda\_function.py

Runtime: Python 3.x

Key behaviors:



Adds CORS headers in every response:



"Access-Control-Allow-Origin": "\*",

"Access-Control-Allow-Headers": "Content-Type,Authorization",

"Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",





Handles these HTTP methods at /notes:



Method	Description

GET	List current user’s notes, or get a single note

POST	Create a new note for the current user

PUT	Update an existing note (only if owned by the user)

DELETE	Delete an existing note (only if owned by the user)

OPTIONS	CORS preflight – returns { "ok": true }



Uses DynamoDB Notes table with partition key:



id (String)





Each note item has the shape:



{

&nbsp; "id": "uuid",

&nbsp; "owner": "<cognito-sub>",

&nbsp; "text": "note text",

&nbsp; "createdAt": "2026-02-18T03:09:22Z",

&nbsp; "updatedAt": "2026-02-18T03:14:04Z"   // only after first update

}





Ownership is enforced on GET (single item), PUT, and DELETE.



4\. Getting an access token (Cognito)



Open the Cognito Hosted UI login URL in a browser.

(It looks like):



https://<your-domain>.auth.ap-southeast-2.amazoncognito.com/login?client\_id=...\&response\_type=code\&scope=email+openid+phone\&redirect\_uri=https%3A%2F%2F<your-cloudfront-domain>





Sign in (or sign up first, then sign in).



When you are redirected to your CloudFront/test page, you’ll see a URL like:



https://d84l1y8p4kdic.cloudfront.net/?code=XXXXXXXX...





That code= is an authorization code.



Exchange the code for tokens with curl:



curl -X POST "https://<your-domain>.auth.ap-southeast-2.amazoncognito.com/oauth2/token" \\

&nbsp; -H "Content-Type: application/x-www-form-urlencoded" \\

&nbsp; -d "grant\_type=authorization\_code\&client\_id=<YOUR\_CLIENT\_ID>\&code=<AUTH\_CODE>\&redirect\_uri=https%3A%2F%2F<your-cloudfront-domain>"





The response includes access\_token, id\_token, and refresh\_token.

For the API calls we use access\_token.



5\. Using the HTML tester (notes.html)



Open notes.html in a browser (double-click it).



Paste your access token into the “Access Token (Bearer)” textarea.



Use the buttons:



List notes (GET) – fetches your notes and shows them in the list.



Create note (POST) – uses “Note text” textarea and adds a new note.



Update note (PUT) – requires a Note ID (click an ID in the list to copy it).



Delete note (DELETE) – deletes the note with the given Note ID.



The bottom panel shows:



HTTP status (e.g. 200 OK, 401 Unauthorized, 404 Not found)



The raw JSON response or any error message.



6\. Calling the API with curl



Assumes:



API URL:

https://ss5k5py93l.execute-api.ap-southeast-2.amazonaws.com/prod/notes



Environment variable TOKEN contains your access token.



List notes (GET)

curl -i -X GET "https://ss5k5py93l.execute-api.ap-southeast-2.amazonaws.com/prod/notes" \\

&nbsp; -H "Authorization: Bearer $TOKEN"



Create note (POST)

curl -i -X POST "https://ss5k5py93l.execute-api.ap-southeast-2.amazonaws.com/prod/notes" \\

&nbsp; -H "Authorization: Bearer $TOKEN" \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{"text":"my first secure note"}'



Update note (PUT)

NOTE\_ID="<existing-note-id>"



curl -i -X PUT "https://ss5k5py93l.execute-api.ap-southeast-2.amazonaws.com/prod/notes?id=$NOTE\_ID" \\

&nbsp; -H "Authorization: Bearer $TOKEN" \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{"text":"updated secure note"}'



Delete note (DELETE)

NOTE\_ID="<existing-note-id>"



curl -i -X DELETE "https://ss5k5py93l.execute-api.ap-southeast-2.amazonaws.com/prod/notes?id=$NOTE\_ID" \\

&nbsp; -H "Authorization: Bearer $TOKEN"



7\. CORS notes



API Gateway HTTP API CORS config:



Allow origin: \*



Allow methods: GET, POST, PUT, DELETE, OPTIONS



Allow headers: authorization, content-type



Lambda also returns matching headers via \_response() to keep things consistent.



If the browser shows "blocked by CORS policy" check:



OPTIONS /notes route exists and returns 200 with the CORS headers.



JWT authorizer is not attached to the OPTIONS route.



Lambda responses for other methods include the same CORS headers.



8\. Future improvements / TODOs



Replace local notes.html file with an S3-hosted static website.



Store access token in localStorage (with a quick “clear” button).



Add pagination or query filtering for notes.



Add unit tests for lambda\_function.py.



Add CI/CD pipeline (SAM, CDK, or Terraform).



9\. Quick start recap



Get a Cognito access token via Hosted UI + /oauth2/token.



Paste the token into notes.html or export it to $TOKEN.



Use Create / List / Update / Delete buttons or curl commands.



All notes are scoped to the authenticated user via the owner field.



Happy hacking 👨‍🔧🛠️





You can:



1\. Create a new file `README.md` in your `notes-api` folder.

2\. Paste everything from the code block above.

3\. Save.



If you want, next we can also add a little \*\*section at the top with your exact Cognito domain + client id\*\* so Future You doesn’t have to dig through the console again.



