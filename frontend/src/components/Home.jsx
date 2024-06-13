import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useAuth } from "../context/auth";
import { NavLink } from "react-router-dom";

function Home() {
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoggedIn)
      navigate("/chats");
  }, []);
  
  if (isLoggedIn)
    return null;

  return (
    <div className="">
      <div className="flex flex-row justify-center">
        <h1 className="flex-initial m-4">
          Welcome to RESTchat
        </h1>
      </div>
      <div className="flex flex-row justify-center">
        <p className="flex-initial py-4 m-4">
          Prepare to have your mind blown with the worlds greatest chat experience!
        </p>
        <NavLink to="/login" className="flex-initial px-2 py-4 m-4 border rounded-xl">
          Get Started
        </NavLink>
      </div>
    </div>
  );
}

export default Home;