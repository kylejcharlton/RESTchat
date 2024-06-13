import { useParams } from "react-router-dom";
import Chat from "./Chat";
import ChatList from "./ChatList";
import "./ChatsPage.css";
import { NavLink } from "react-router-dom";


function ChatsPage() {
  const {chatID} = useParams();
  return (
    <div id="chat-page-container" className="py-5">
      <div id="chat-list-col">
        <h1>Chats</h1>
        <ChatList selected={chatID}/>
      </div>
      <div id="chat-messages-col">
        <div className="flex flex-row justify-between w-full px-4">
          <h1>Messages</h1>
          {chatID &&
            <NavLink to={`/chats/${chatID}/details`} className="mt-auto h-fit hover:text-slate-300">Details</NavLink>
          }
        </div>
        <Chat chatID={chatID}/>
      </div>
    </div>
  );
}

export default ChatsPage;