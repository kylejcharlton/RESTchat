import { useQuery } from "react-query";
import PropTypes from 'prop-types';
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/auth";


function ChatItem({ id, name, created_at, className }) {
  const timestamp = new Date(created_at);

  return (
    <Link className={`${className} chat-item`} id={id} to={`/chats/${id}`}>
      <div className="chat-item-name">{name}</div>
      <div className="chat-item-date">created at: {timestamp.toDateString()}</div>
    </Link>
  );
}


function ChatList({ selected }) {
  const { token } = useAuth();
  const { data, status } = useQuery({
    queryKey: ["chats"],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/chats`, {
        headers: { "Authorization": "Bearer " + token }
      });
      return await res.json();
    },
  });

  if (status === "loading")
    return (
      <div className="chat-list-container">
        <h2 style={{margin: "0.25em 0.75em"}}>Loading...</h2>
      </div>
    );
  
  if (status === "error")
    return (
      <div className="chat-list-container">
        <h2 style={{margin: "0.25em 0.75em"}}>An error has occurred.</h2>
      </div>
    );


  return (
    <>
      <div className="chat-list-container">
        {data.chats?.map((c) => {
            return <ChatItem className={c.id === selected ? "selected" : ""} key={c.id} {...c} />;
        })}
      </div>
      <div className="flex flex-row justify-center px-3 py-2">
        <NavLink to="/chats/new" className="flex-none w-full p-3 m-1 text-center border rounded-lg hover:bg-slate-800">New Chat</NavLink>
      </div>
    </>
  );
}

ChatList.propTypes = {
  selected: PropTypes.string,
};

export default ChatList;