import { useState } from "react";
import { useQueryClient, useMutation } from "react-query";
import { useAuth } from "../context/auth";
import FormInput from "./FormInput";
import Button from "./Button";
import { useNavigate } from "react-router-dom";

function CreateChat() {
  const queryClient = useQueryClient();
  const { token } = useAuth();
  const [ chatName, setChatName ] = useState("");
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: () => (
      fetch(
        `http://127.0.0.1:8000/chats`,
        {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: chatName
          }),
        },
      ).then((response) => response.json())
    ),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["chats"],
      });

      navigate(`/chats/${data.chat.id}/details`);
    },
  });

  const onSubmit = (e) => {
    e.preventDefault();
    mutation.mutate();
  }

  return (
    <div className="w-1/2 p-4 m-6 mx-auto border-2 rounded-xl">
      <form className="w-fill" onSubmit={onSubmit}>
        <FormInput name="Chat Name" value={chatName} setter={setChatName} />
        <Button type="submit" onClick={onSubmit}>Create</Button>
      </form>
    </div>
  );
}

export default CreateChat;