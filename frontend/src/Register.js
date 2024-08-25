import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const USER_REGEX = /^[a-zA-Z][a-zA-Z0-9-_]{3,23}$/;
const PWD_REGEX = /^(?=.*[0-9])[A-Za-z\d]{8,}$/;

const Register = () => {
    const userRef = useRef();
    const errRef = useRef();
    const navigate = useNavigate();

    const [username, setUsername] = useState('');
    const [validUsername, setValidUsername] = useState(false);

    const [email, setEmail] = useState('');
    const [validEmail, setValidEmail] = useState(false);

    const [password, setPassword] = useState('');
    const [validPassword, setValidPassword] = useState(false);

    const [matchPwd, setMatchPwd] = useState('');
    const [validMatch, setValidMatch] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef.current.focus();
    }, []);

    useEffect(() => {
        setValidEmail(EMAIL_REGEX.test(email));
        if (email && !validEmail) {
            setErrMsg("Email must be a valid email address.");
        }
    }, [email, validEmail]);

    useEffect(() => {
        setValidUsername(USER_REGEX.test(username));
        if (username && !validUsername) {
            setErrMsg("Username must be 4 to 24 characters long, start with a letter, and can include letters, numbers, underscores, and hyphens.");
        }
    }, [username, validUsername]);

    useEffect(() => {
        setValidPassword(PWD_REGEX.test(password));
        setValidMatch(password === matchPwd);
        if (password && !validPassword) {
            setErrMsg("Password must be at least 8 characters long and include at least one number.");
        }
        if (matchPwd && !validMatch) {
            setErrMsg("Passwords do not match.");
        }
    }, [password, matchPwd, validPassword, validMatch]);

    useEffect(() => {
        setErrMsg('');
    }, [username, email, password, matchPwd]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const v1 = USER_REGEX.test(username);
        const v2 = EMAIL_REGEX.test(email);
        const v3 = PWD_REGEX.test(password);
        if (!v1 || !v2 || !v3 || !validMatch) {
            setErrMsg("Register Gagal! \n mohon periksa kembali");
            return;
        }
        // Handle registration logic here
        console.log(username, email, password);
        setSuccess(true);
        navigate('/login'); // Redirect to Login page after successful registration
    }

    return (
        <div style={{ display: 'flex', justifyContent: 'center', textAlign: 'center', flexDirection: 'column', alignItems: 'center', minHeight: '100vh' }}>
            {success ? (
                <section>
                    <h1>Success!</h1>
                    <p>
                        <a href="/login">Sign In</a>
                    </p>
                </section>
            ) : (
                <section style={{ maxWidth: '400px', width: '100%' }}>
                    <h1 style={{ marginBottom: '20px' }}>Register</h1>
                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        
                        <label htmlFor="email" style={{ alignSelf: 'flex-start' }}>Email:</label>
                        <input
                            type="email"
                            id="email"
                            onChange={(e) => setEmail(e.target.value)}
                            value={email}
                            required
                            aria-invalid={validEmail ? "false" : "true"}
                            ref={userRef}
                            style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
                        />

                        <label htmlFor="username" style={{ alignSelf: 'flex-start' }}>Username:</label>
                        <input
                            type="text"
                            id="username"
                            autoComplete="off"
                            onChange={(e) => setUsername(e.target.value)}
                            value={username}
                            required
                            aria-invalid={validUsername ? "false" : "true"}
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

                        <label htmlFor="confirm_pwd" style={{ alignSelf: 'flex-start' }}>Confirm Password:</label>
                        <input
                            type="password"
                            id="confirm_pwd"
                            onChange={(e) => setMatchPwd(e.target.value)}
                            value={matchPwd}
                            required
                            aria-invalid={validMatch ? "false" : "true"}
                            style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
                        />

                        <button style={{ padding: '10px 20px', marginTop: '20px' }}>Sign Up</button>
                    </form>
                    {errMsg && (
                        <p ref={errRef} style={{ color: 'red', marginTop: '20px' }} aria-live="assertive">
                            {errMsg}
                        </p>
                    )}
                    <p style={{ marginTop: '20px' }}>
                        Already registered?<br />
                        <span className="line">
                            <a href="/login">Sign In</a>
                        </span>
                    </p>
                </section>
            )}
        </div>
    )
}

export default Register;
