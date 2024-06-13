import { useEffect, useState } from "react";
import { useAuth } from "../context/auth";
import { useUser } from "../context/user";
import FormInput from "./FormInput";
import Button from "./Button";

function Profile() {
  const { logout } = useAuth();
  const user = useUser();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [created, setCreated] = useState("");

  const reset = () => {
    if (user) {
      setUsername(user.username);
      setEmail(user.email);
      setCreated((new Date(user.created_at).toDateString()));
    }
  }

  useEffect(reset, [user]);


  return (
    <div className="px-4 py-8 mx-auto max-w-96">
      <h2 className="py-2 text-2xl font-bold">
        Details
      </h2>
      <form className="px-4 py-2 border rounded">
        <FormInput
          name="Username"
          type="text"
          value={username}
          readOnly={true}
        />
        <FormInput
          name="Email"
          type="email"
          value={email}
          readOnly={true}
        />
        <FormInput
          name="Member since"
          type="text"
          value={created}
          readOnly={true}
        />
      </form>
      <Button onClick={logout}>
        Logout
      </Button>
    </div>
  );
}

export default Profile;