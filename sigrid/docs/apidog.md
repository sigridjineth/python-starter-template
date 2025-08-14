
Send Chat (stream)
Developing
POST
/api/v2/answer/stream
Request
cURL
cURL-Windows
Httpie
wget
PowerShell
curl --location --request POST '/api/v2/answer/stream' \
--header 'Content-Type: application/json' \
--header 'storm-api-key;' \
--data-raw '{
    "question": "string",
    "bucketIds": [
        "bbb"
    ],
    "threadId": "string"
}'
Response
data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"contexts":[{"id":"4267133562605706001","type":"document","bucketName":"test2","fileName":"2022 Wire Rod Catalog_Eng_Final.pdf","pageName":"3","context":"stainless steels. The company’s global competitiveness was further enhanced when we opened the world’s first FINEX commercialization facility in May 2007. 4 5 Main products _ Hot-rolled steel, Plate, Cold-rolled steel, Wire rod, Electrical steel, Stainless steel, API steel, etc. Crude steel production _ 16,852","referenceIdx":1},{"id":"4267133562605706001","type":"document","bucketName":"test2","fileName":"2022 Wire Rod Catalog_Eng_Final.pdf","pageName":"12","context":".60 POSCORD70M 0.67~0.75 0.10~0.30 0.40~0.60 0.03 Max. 0.03 Max. POSHIS120L 0.46~0.60 1.20~1.70 0.50~0.80 0.025 Max. 0.025 Max. 0.50~0.80 POSCORD70D 0.67~0.75 0.10~0.30 0.40~0.60 0.03 Max. 0.03 Max. POSHIS120S 0.50~0.56 1.20~1.60 0.50~0.90 0.020 Max. 0.020 Max. 0.50~0.80 POSCORD80S 0.78~0.85 0.10~0.30 0.40~0.60 0.","referenceIdx":2},{"id":"4267133562605706001","type":"document","bucketName":"test2","fileName":"2022 Wire Rod Catalog_Eng_Final.pdf","pageName":"15","context":"ang-gil, Gwangyang-si, Jeollanam-do, 57807 Republic of Korea TEL 82-61-790-0114 FAX 82-61-790-7000 www.posco.com www.steel-n.com","referenceIdx":3}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"role":"assistant","content":""}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"죄"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"송"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"합니다"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"."}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 제가"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 배우"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"지"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 못"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"한"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 내용"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"이라"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"서"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 답"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"변"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"을"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 드"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"릴"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 수"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":" 없습니다"}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{"content":"."}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[{"index":0,"delta":{}}]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-stream","data":{"id":"7252980379129741312","createdAt":"2024-10-18T09:54:36.243Z","updatedAt":"2024-10-18T09:54:36.243Z","threadId":"7252980378794196992","question":"신노스케에 대해 자세히 알려줘.","choices":[]}}}

data: {"status":"success","data":{"sseEventOperation":"create-chat-log-finished","data":{}}}
Request
Authorization
Add parameter in header storm-api-key
Example:
storm-api-key: ********************
Body Params
application/json
question
string 
required
chat question text
bucketIds
array[string]
asd
optional
target bucket ID for the question. if empty, the question will target all buckets
threadId
string 
optional
thread ID to send the chat to. if not provided, a new thread will be created internally
Examples
Responses
🟢200
Success
text/event-stream
status
string 
required
data
object 
required
chat
object 
required
contexts
array [object {8}] 
required
Modified at about 2 months ago
Previous
Send Chat (non-stream)
Next
Search Context
Built with


--------

m)
Developing
POST
/api/v2/answer
Request
cURL
cURL-Windows
Httpie
wget
PowerShell
curl --location --request POST '/api/v2/answer' \
--header 'Content-Type: application/json' \
--header 'storm-api-key;' \
--data-raw '{
    "question": "string",
    "bucketIds": [
        "bbb"
    ],
    "threadId": "string",
    "webhookUrl": "string"
}'
Response
{
    "status": "consequat in dolor ut",
    "data": {
        "chat": {
            "id": "1",
            "threadId": "amet quis fugiat enim eu",
            "question": "consequat in minim exercitation",
            "answer": "nulla nisi non aliqua",
            "createdAt": "2024-10-17T19:19:51.000Z",
            "updatedAt": "2024-10-17T11:18:08.563Z",
            "status": "success"
        },
        "contexts": [
            {
                "id": "1",
                "type": "document",
                "bucketName": "brevis delicate arcus",
                "fileName": "voluntarius alveus tibi",
                "pageName": "via coruscus defluo",
                "context": "consequat labore",
                "referenceIdx": 1
            }
        ]
    }
}
Request
Authorization
Add parameter in header storm-api-key
Example:
storm-api-key: ********************
Body Params
application/json
question
string 
required
chat question text
bucketIds
array[string]
asd
optional
target bucket ID for the question. if empty, all buckets are used
threadId
string 
optional
thread ID to send the chat to. if omitted, a new thread will be created automatically
webhookUrl
string 
optional
webhook to receive the result
Examples
Responses
🟢200
Success
application/json
status
string 
required
data
object 
required
chat
object ([object] chat) 
required
contexts
array[object ([object] context) {7}] 
required
Modified at about 2 months ago
Previous
Delete Document
Next
Send Chat (stream)


--------------

Chat
Search Context
Developing
POST
/api/v2/answer/context
Searches for sentences semantically closest to the question text from trained documents in the bucket.
Request
cURL
cURL-Windows
Httpie
wget
PowerShell
curl --location --request POST '/api/v2/answer/context' \
--header 'Content-Type: application/json' \
--header 'storm-api-key;' \
--data-raw '{
    "question": "string",
    "bucketIds": [
        "string"
    ],
    "threadId": "string"
}'
Response
{
    "status": "success",
    "data": {
        "contexts": [
            {
                "id": "anim dolor non tempor Ut",
                "chatId": "enim quis",
                "type": "consectetur anim Lorem",
                "bucketName": "ara capillus tener",
                "fileName": "terra pauper torrens",
                "pageName": "trucido similique atavus",
                "context": "deserunt proident sed labore sint",
                "referenceIdx": 1
            },
            {
                "id": "Lorem commodo",
                "chatId": "irure",
                "type": "nisi sint id",
                "bucketName": "desidero aureus aetas",
                "fileName": "coniecto absque claustrum",
                "pageName": "paulatim arceo ut",
                "context": "veniam",
                "referenceIdx": 2
            }
        ]
    }
}
Request
Authorization
Add parameter in header storm-api-key
Example:
storm-api-key: ********************
Body Params
application/json
question
string 
required
question text
bucketIds
array[string]
optional
target bucket ID to search for related chunks. if empty, all buckets will be searched
threadId
string 
optional
thread ID with chat context. if not provided, a new thread will be created internally
Examples
Responses
🟢200
Success
application/json
status
string 
required
success / error
data
object 
required
contexts
array[object ([object] context) {7}] 
required
Modified at about 2 months ago
Previous
Send Chat (stream)
Next
/convert/md
Built with