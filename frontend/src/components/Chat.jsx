import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import ScrollContainer from "./ScrollContainer";
import FormInput from "./FormInput";
import Button from "./Button";
import { useAuth } from "../context/auth";
import { useUser } from "../context/user";


function Message({created_at, user, text, onDelete, onEdit, canEdit}) {
  const timestamp = new Date(created_at);
  const [ editedText, setEditedText ] = useState(text);
  const [ editing, setEditing ] = useState(false);

  const editCallback = (e) => {
    e.preventDefault();
    onEdit(editedText);
    setEditing(false);
  };

  const cancelEditing = () => {
    setEditing(false);
    setEditedText(text);
  };

  return (
    <div className="chat-message-container">
      <div className="chat-message-header">
        <div className="chat-message-user">{user.username}</div>
        <div className="chat-message-timestamp">{timestamp.toDateString()} &ndash; {timestamp.toLocaleTimeString()}</div>
      </div>
      <div className="flex flex-row w-fill">
        { editing ?
          <>
            { canEdit &&
              <form className="flex flex-row justify-between flex-1" onSubmit={editCallback}>
                <FormInput className="mr-10 break-words w-fill h-fill" value={editedText} setter={setEditedText} />
                <Button type="submit">Save</Button>
              </form>
            }
          </>
          :
          <div className="flex-1 pr-8 chat-message-contents">{text}</div>
        }
        { canEdit &&
          <div>
            {editing ?
              <Button onClick={cancelEditing}>Cancel</Button>
              :
              <div className="">
                <Button onClick={() => setEditing(true)}>Edit</Button>
                <Button onClick={onDelete}>Delete</Button>
              </div>
            }
          </div>
        }
      </div>
    </div>
  );
}


function Chat({ chatID }) {
  const queryClient = useQueryClient();
  const [ chatBox, setChatBox ] = useState("");
  const { token } = useAuth();
  const currentUser = useUser();
  
  const { data, status } = useQuery({
    queryKey: ["chats", chatID],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/chats/${chatID}/messages`, {
        headers: { "Authorization": "Bearer " + token }
      });
      return await res.json();
    },
    enabled: chatID != undefined,
  });

  const mutation = useMutation({
    mutationFn: () => (
      fetch(
        `http://127.0.0.1:8000/chats/${chatID}/messages`,
        {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: chatBox,
          }),
        },
      ).then((response) => response.json())
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chats", chatID],
      });
      setChatBox("");
    },
  });

  const messageDeleteMutation = useMutation({
    mutationFn: (messageID) => (
      fetch(
        `http://127.0.0.1:8000/chats/${chatID}/messages/${messageID}`,
        {
          method: "DELETE",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
        },
      )
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chats", chatID],
      });
    },
  });

  const messageEditMutation = useMutation({
    mutationFn: ({ messageID, updatedText }) => (
      fetch(
        `http://127.0.0.1:8000/chats/${chatID}/messages/${messageID}`,
        {
          method: "PUT",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: updatedText
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


  const onSend = (e) => {
    e.preventDefault();
    mutation.mutate()
  }

  if (chatID == undefined)
    return (
      <div className="chat-container">
        <h2 style={{margin: "0.25em 0.75em"}}>Select a chat.</h2>
      </div>
    );

  if (status === "loading")
    return (
      <div className="chat-container">
        <h2 style={{margin: "0.25em 0.75em"}}>Loading...</h2>
      </div>
    );
  
  if (status === "error")
    return (
      <div className="chat-container">
        <h2 style={{margin: "0.25em 0.75em"}}>An error has occurred.</h2>
      </div>
    );

  const onMessageDelete = (messageID) => {
    messageDeleteMutation.mutate(messageID);
  };

  const onMessageEdit = (messageID, updatedText) => {
    messageEditMutation.mutate({messageID, updatedText});
  };
  
  return (
    <>
      <ScrollContainer className="chat-container">
          {data.messages?.map((m) => {
            return <Message canEdit={m.user.id === currentUser.id} onEdit={(updatedText) => onMessageEdit(m.id, updatedText)} onDelete={() => onMessageDelete(m.id)} key={m.id} {...m} />;
          })}
          { !data.meta?.count &&
            <h2 className="p-2">There's nothing here. Start chatting using the textbox below.</h2>
          }
      </ScrollContainer>
      <form className="flex flex-row ml-3">
        <FormInput type="text" setter={setChatBox} value={chatBox} />
        <Button className="flex flex-col flex-none mx-2" type="submit" onClick={onSend}>
          Send
        </Button>
      </form>
    </>
  );
}

export default Chat;