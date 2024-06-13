import { Form, NavLink, useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { useAuth } from "../context/auth";
import FormInput from "./FormInput";
import Button from "./Button";
import { useState } from "react";
import { useUser } from "../context/user";

function ChatNamePanel({ chatID }) {
  const queryClient = useQueryClient();
  const { token } = useAuth();
  const [ currentChatName, setCurrentChatName ] = useState("");
  const currentUser = useUser();

  const { data, isLoading } = useQuery({
    queryKey: ["chats", chatID],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/chats/${chatID}`, {
        headers: { "Authorization": "Bearer " + token }
      });
      return await res.json();
    },
    onSuccess: (data) => {
      setCurrentChatName(data.chat?.name);
    }
  });

  const mutation = useMutation({
    mutationFn: () => (
      fetch(
        `http://127.0.0.1:8000/chats/${chatID}`,
        {
          method: "PUT",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: currentChatName,
          }),
        },
      ).then((response) => response.json())
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chats", chatID],
      });
    },
  });

  const onSubmit = () => {
    mutation.mutate();
  }

  if (isLoading)
    return null;

  return (
    <div className="w-1/2 p-4 m-6 mx-auto border-2 rounded-xl">
      <h2>Chat Name</h2>
      <div>
        <FormInput className="" setter={setCurrentChatName} onSubmit={onSubmit} value={currentChatName} disabled={data.chat?.owner.id !== currentUser.id }/>
        { data.chat?.owner.id === currentUser.id &&
          <Button disabled={currentChatName === data.chat?.name} onClick={onSubmit}>Update</Button>
        }
      </div>
    </div>
  );
}


function ChatUsersPanel({ chatID }) {
  const queryClient = useQueryClient();
  const { token } = useAuth();
  const [ selectedUser, setSelectedUser ] = useState("none");
  const currentUser = useUser();

  const chat = useQuery({
    queryKey: ["chats", chatID, "?include=users"],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/chats/${chatID}?include=users`, {
        headers: { "Authorization": "Bearer " + token }
      });
      return await res.json();
    }
  });

  const users = useQuery({
    queryKey: ["users"],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/users`, {
        headers: { "Authorization": "Bearer " + token }
      });
      return await res.json();
    }
  });

  const addUserMutation = useMutation({
    mutationFn: () => (
      fetch(
        `http://127.0.0.1:8000/chats/${chatID}/users/${selectedUser}`,
        {
          method: "PUT",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
        },
      ).then((response) => response.json())
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chats", chatID, "?include=users"],
      });
    },
  });

  const removeUserMutation = useMutation({
    mutationFn: (userID) => (
      fetch(
        `http://127.0.0.1:8000/chats/${chatID}/users/${userID}`,
        {
          method: "DELETE",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
        },
      ).then((response) => response.json())
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chats", chatID, "?include=users"],
      });
    },
  });

  const onAddUser = (e) => {
    e.preventDefault();
    addUserMutation.mutate();
    setSelectedUser("none");
  };

  if (chat.isLoading || users.isLoading)
    return null;


  return (
    <div className="w-1/2 p-4 m-6 mx-auto border-2 rounded-xl">
      <h2>Users</h2>
      <div className="p-6">
        <div>
          {chat.data.users?.map((u) => {
            return (
              <div className="flex flex-row justify-between mx-12" key={u.id}>
                <div className="my-auto h-fit text-sky-300">{u.username}</div>
                { u.id !== chat.data.chat?.owner.id ?
                  <>
                    { currentUser.id === chat.data?.chat.owner.id &&
                      <Button onClick={() => {removeUserMutation.mutate(u.id)}}>Remove</Button>
                    }
                  </>
                  :
                  <Button disabled>Owner</Button>
                }
              </div>
            );
          })}
        </div>
        { currentUser.id === chat.data?.chat.owner.id &&
          <form className="flex flex-row justify-center" onSubmit={onAddUser}>
            <select className="w-1/4 h-6 my-auto" select={selectedUser} value={selectedUser} onChange={e => setSelectedUser(e.target.value)}>
              <option value="none">Select a user</option>
              {users.data.users?.map((u) => {
                if (!chat.data?.users.find(e => e.id === u.id))
                  return <option key={u.id} value={u.id}>{u.username}</option>
              })}
            </select>
            <div className="w-8"></div>
            <Button type="submit" onClick={onAddUser} disabled={selectedUser === "none"}>Add user</Button>
          </form>
        }
      </div>
    </div>
  );
}


function ChatDetails() {
  const { chatID } = useParams();

  return (
    <div>
      <ChatNamePanel chatID={chatID} />
      <ChatUsersPanel chatID={chatID} />
    </div>
  );
}

export default ChatDetails;