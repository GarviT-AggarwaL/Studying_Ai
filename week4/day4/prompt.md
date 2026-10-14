I am buildng an restaurant order management ai sgent system using langgraph.
i will explain you very clearly what i want in the architecture . i will also explain you the nodes, the states and the edges.
in the end i will give you test cases to simulate and to tell whether it pass or not.
the rough plan is :
there will be a user, when the code runs the user will give an order.
this willl be ttaken as input which i will type. thiss should go to llm
the order should go to llm . the order as of now hshould contain dish and the required quantity.
for simplicity purpose for now will limit the order to one particular dish and whatever quantity the user wants.
the llm will have to extract the order name, quantity from the user input.
if the user input is unrralted to food ordering thr llm should not process that and tell the user the same hing that is i am ai agent of food ordering and not a general purpose llm.
once the llm has order the dish and quantity
it will send that that to a node called order_confirm.
the task of this order confirm is to look at the menu (i will tell you the menu later in this prompt).
then this node will decide one of 3 cases.
the order is avalaible
the order is partially avalaible meanss quantity is not sufficient.
the order is not avalaible at all(dish being not in the menu or being 0 qauntity is unavalaible)
it will put this to the sateus of the state(i will tell u exact content of the langgraph as well)
once the llm received this
if the status is confirmened (full avalaible) it should call another node called cook
if the status is partial or not avalabile it should again prompty the user to decide
the user can either place a new order or can confirm if he wants to go ahead with the partial order

this order retries will be limitwd to 3 attempts meaning if after 3 attempts the user is not satisfied the ssytem will come to the END node
now when cook node is called
there can be two case
wither the cook is done then the status will be ready
and if cook fails(we can juse a prob func) give 40% chance of fail and 60% to success
if the cook fails there should be 1 more attempt allowed for cook to succeed if the cook fails even aftert these
then the llm should issue a aplogy to user and come to end state
if the cook succeeds the status will be READY
and the next node will be called which is serve
serve pass or serve fail 
this also hai 2 attemopts if the serve fail two time then llm should issue apology to user and com to end state
if serve succeed the status shjould become complete the llm should issue a msg to uyser saying your order is compplete.
if serve fails then cook should becalled one more time to retry.
note that if cook has exhausted its retry attempts then it should not cook again and llm should issue an apology and come to end state
now the state of langgraph
there should be annotated msg between llm and user
there should be order details
dish name as str
required quantity as int
avalaible quantity as str
order_confirm will write the avalaible quantity by reading the menu
the llm should get to know the order confirm status by reading the state
if a dish is not avalaible in the menu then order confirm should write 0 as avail quantity
then there should be status
eaxh node will update the status as specified in the aove rules
then order retry attempts are 3
cookn retry attempts whivch are 2
serve retry attempts which are 2
each time a failure happened and node is retrying it should discrent the counter 
if any retry counter becomes 0 it means it is over.llm should understand whenter it has to give a retry or issue aplogy by reading the counter
in the end there should be final result whter order si finally completed opr not
use groqmodel openai/gpt-oss-120b and my api keys are in .env file 
this is the menu
burger 10
pizza 20
momos 4

write the code and ask if there are any open questions from your side then ask
i will give you some test cases to test later on