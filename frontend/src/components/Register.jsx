import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/auth";
import FormInput from "./FormInput";
import Button from "./Button";

function Error({ message }) {
  if (message === "") {
    return <></>;
  }
  return (
    <div className="text-xs text-red-300">
      {message}
    </div>
  );
}

function LoginLink() {
  return (
    <div className="flex flex-col pt-8">
      <div className="text-xs">
        Already have an account?
      </div>
      <Link to="/login">
        <Button className="w-full mt-1">
          Login
        </Button>
      </Link>
    </div>
  );
}

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const disabled = username === "" || email === "" || password === "";

  const onSubmit = (e) => {
    e.preventDefault();

    fetch(
      "http://127.0.0.1:8000/auth/registration",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password }),
      },
    ).then((response) => {
      if (response.ok) {
        navigate("/login");
      } else if (response.status === 422) {
        response.json().then((data) => {
          setError(data.detail.entity_field + " already taken");
        });
      } else {
        setError("error logging in");
      }
    });
  }

  return (
    <div className="px-4 py-8 mx-auto max-w-96">
      <form onSubmit={onSubmit}>
        <FormInput type="text" name="Username" setter={setUsername} />
        <FormInput type="email" name="Email" setter={setEmail} />
        <FormInput type="password" name="Password" setter={setPassword} />
        <Button className="w-full" type="submit" disabled={disabled}>
          Register
        </Button>
        <Error message={error} />
      </form>
      <LoginLink />
    </div>
  );
}

export default Register;