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

function RegistrationLink() {
  return (
    <div className="flex flex-col pt-8">
      <div className="text-xs">
        Need an account?
      </div>
      <Link to="/register">
        <Button className="w-full mt-1">
          Register
        </Button>
      </Link>
    </div>
  );
}

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const { login } = useAuth();

  const disabled = username === "" || password === "";

  const onSubmit = (e) => {
    e.preventDefault();

    fetch(
      "http://127.0.0.1:8000/auth/token",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ username, password }),
      },
    ).then((response) => {
      if (response.ok) {
        response.json().then(login);
        navigate("/");
      } else if (response.status === 401) {
        response.json().then((data) => {
          setError(data.detail.error_description);
        });
      } else {
        setError("Error logging in");
      }
    });
  };

  return (
    <div className="px-4 py-8 mx-auto max-w-96">
      <form onSubmit={onSubmit}>
        <FormInput type="text" name="Username" setter={setUsername} />
        <FormInput type="password" name="Password" setter={setPassword} />
        <Button className="w-full" type="submit" disabled={disabled}>
          login
        </Button>
        <Error message={error} />
      </form>
      <RegistrationLink />
    </div>
  );
}

export default Login;