import { useRef, useState, useEffect } from "react";
import { Link } from "react-router-dom";

const USER_REGEX = /^[a-zA-Z][a-zA-Z0-9-_]{3,23}$/;
const PWD_REGEX = /^(?=.*[0-9])[A-Za-z\d]{8,}$/;

const Login = () => {
    const userRef = useRef();
    const errRef = useRef();

    const [username, setUsername] = useState('');
    const [validUsername, setValidUsername] = useState(false);

    const [password, setPassword] = useState('');
    const [validPassword, setValidPassword] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef.current.focus();
    }, []);

    useEffect(() => {
        setValidUsername(USER_REGEX.test(username));
        if (username && !validUsername) {
            setErrMsg("Username must be 4 to 24 characters long, start with a letter, and can include letters, numbers, underscores, and hyphens.");
        }
    }, [username, validUsername]);

    useEffect(() => {
        setValidPassword(PWD_REGEX.test(password));
        if (password && !validPassword) {
            setErrMsg("Password must be at least 8 characters long and include at least one number.");
        }
    }, [password, validPassword]);

    useEffect(() => {
        setErrMsg('');
    }, [username, password]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const v1 = USER_REGEX.test(username);
        const v2 = PWD_REGEX.test(password);
        if (!v1 || !v2) {
            setErrMsg("Login Gagal!");
            return;
        }
        // Handle login logic here
        console.log(username, password);
        setSuccess(true);
    }

    return (
        <div style={{ display: 'flex', justifyContent: 'center', textAlign: 'center', flexDirection: 'column', alignItems: 'center', minHeight: '100vh' }}>
            {success ? (
                <section>
                    <h1>Login Successful!</h1>
                    <p>
                        <a href="#">Go to Dashboard</a>
                    </p>
                </section>
            ) : (
                <section style={{ maxWidth: '400px', width: '100%' }}>
                    <h1 style={{ marginBottom: '20px' }}>Login</h1>
                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        
                        <label htmlFor="username" style={{ alignSelf: 'flex-start' }}>Username:</label>
                        <input
                            type="text"
                            id="username"
                            onChange={(e) => setUsername(e.target.value)}
                            value={username}
                            required
                            aria-invalid={validUsername ? "false" : "true"}
                            ref={userRef}
                            style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
                        />

                        <label htmlFor="password" style={{ alignSelf: 'flex-start' }}>Password:</label>
                        <input
                            type="password"
                            id="password"
                            onChange={(e) => setPassword(e.target.value)}
                            value={password}
                            required
                            aria-invalid={validPassword ? "false" : "true"}
                            style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
                        />

                        <button style={{ padding: '10px 20px', marginTop: '20px' }}>Log In</button>
                    </form>
                    {errMsg && (
                        <p ref={errRef} style={{ color: 'red', marginTop: '20px' }} aria-live="assertive">
                            {errMsg}
                        </p>
                    )}
                    <p style={{ marginTop: '20px' }}>
                        Don't have an account?<br />
                        <span className="line">
                            <Link to="/register">Register Here</Link>
                        </span>
                    </p>
                </section>
            )}
        </div>
    )
}

export default Login;
