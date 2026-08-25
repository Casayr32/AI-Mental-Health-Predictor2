import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, registerPatient, registerDoctor, forgotPassword, resetPassword } from '../services/api';

// Toast helper (DOM fallback)
const toast = (msg, type = 'info') => {
    const box = document.getElementById('toastBox');
    if (!box) return;
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.innerHTML = `<i class="ti ti-${type === 'success' ? 'check' : type === 'error' ? 'x' : 'info-circle'}"></i> ${msg}`;
    box.appendChild(t);
    setTimeout(() => {
        t.classList.add('out');
        setTimeout(() => t.remove(), 300);
    }, 3000);
};

export default function Login({ setUser }) {
    const navigate = useNavigate();

    // Auth States
    const [role, setRole] = useState('patient');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [fName, setFName] = useState('');
    const [mName, setMName] = useState('');
    const [lName, setLName] = useState('');
    const [confirmPass, setConfirmPass] = useState('');
    const [specialisation, setSpecialisation] = useState('');

    // Forgot Password States
    const [isForgotPass, setIsForgotPass] = useState(false);
    const [resetStep, setResetStep] = useState(1);
    const [resetToken, setResetToken] = useState('');
    const [newPass, setNewPass] = useState('');

    const clearAllInputs = () => {
        setEmail('');
        setPassword('');
        setFName('');
        setMName('');
        setLName('');
        setConfirmPass('');
        setSpecialisation('');
        setResetToken('');
        setNewPass('');
    };

    const getBackendRole = (r) => {
        if (r === 'admin') return 'Admin';
        if (r === 'clinician') return 'Doctor';
        return 'Patient';
    };

    const getRoutePrefix = (r) => {
        if (r === 'Admin') return 'admin';
        if (r === 'Doctor') return 'doctor';
        return 'patient';
    };

    const saveAuthData = (userData) => {
        localStorage.setItem('user', JSON.stringify(userData));
        if (userData.token) {
            localStorage.setItem('token', userData.token);
        }
        setUser(userData);
    };

    const handleAuth = async (e) => {
        e.preventDefault();
        console.log("--> handleAuth triggered!", { isRegistering, email, role }); // Debug line

        if (isRegistering && password !== confirmPass) {
            return toast('Passwords do not match', 'error');
        }

        try {
            let res;
            const backendRole = getBackendRole(role);

            if (isRegistering) {
                if (role === 'patient') {
                    res = await registerPatient({ first_name: fName, mid_name: mName, last_name: lName, email, password });

                    const userData = {
                        ...(res.data || {}),
                        role: backendRole,
                        first_name: fName,
                        mid_name: mName,
                        last_name: lName
                    };
                    saveAuthData(userData);

                    clearAllInputs();
                    toast('Registration successful! Welcome to MindCare AI.', 'success');
                    navigate(`/${getRoutePrefix(backendRole)}/dashboard`);

                } else if (role === 'clinician') {
                    res = await registerDoctor({ first_name: fName, mid_name: mName, last_name: lName, email, password, specialisation });

                    toast('Registration submitted! Awaiting Admin approval.', 'success');
                    setIsRegistering(false);
                    clearAllInputs();
                }
            } else {
                res = await loginUser({ email, password, role: backendRole });

                const userData = { ...(res.data || {}), role: backendRole };
                saveAuthData(userData);

                clearAllInputs();
                toast(`Welcome back, ${userData.first_name || 'User'}!`, 'success');
                navigate(`/${getRoutePrefix(backendRole)}/dashboard`);
            }
        } catch (error) {
            console.error("Auth Error:", error);
            toast(error.response?.data?.message || 'Authentication failed', 'error');
        }
    };

    const handleForgotPass = async (e) => {
        e.preventDefault();
        try {
            if (resetStep === 1) {
                await forgotPassword(email);
                toast('Token sent to your email! Please check your inbox.', 'success');
                setResetStep(2);
            } else {
                if (newPass.length < 6) return toast('Password must be at least 6 characters', 'error');
                await resetPassword(resetToken, newPass);
                toast('Password reset successfully! Please log in.', 'success');
                resetForgotPass();
            }
        } catch (error) {
            toast(error.response?.data?.message || 'Reset failed', 'error');
        }
    };

    const resetForgotPass = () => {
        setIsForgotPass(false);
        setResetStep(1);
        clearAllInputs();
    };

    if (isForgotPass) {
        return (
            <div className="screen active">
                <div className="login-bg">
                    <div className="login-card">
                        <div className="login-logo">Reset Password</div>
                        <div className="login-sub">
                            {resetStep === 1
                                ? 'Enter your account email to receive a reset token.'
                                : 'Enter the token from your email and your new password.'}
                        </div>

                        <form onSubmit={handleForgotPass} autoComplete="off">
                            {resetStep === 1 ? (
                                <div className="fg">
                                    <label className="fl">Email address</label>
                                    <input className="fi" type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
                                </div>
                            ) : (
                                <>
                                    <div className="fg">
                                        <label className="fl">Reset Token</label>
                                        <input className="fi" type="text" required value={resetToken} onChange={e => setResetToken(e.target.value)} placeholder="Paste token from email" />
                                    </div>
                                    <div className="fg">
                                        <label className="fl">New Password</label>
                                        <input className="fi" type="password" required value={newPass} onChange={e => setNewPass(e.target.value)} placeholder="Min 6 characters" />
                                    </div>
                                </>
                            )}

                            <button type="submit" className="btn btn-pri btn-lg btn-block">
                                {resetStep === 1 ? 'Send Reset Token' : 'Update Password'} <i className="ti ti-arrow-right"></i>
                            </button>

                            <div style={{ marginTop: '12px', textAlign: 'center' }}>
                                <button type="button" className="btn btn-ghost btn-sm" onClick={resetForgotPass}>
                                    <i className="ti ti-arrow-left"></i> Back to Login
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="screen active" id="scr-login">
            <div className="login-bg">
                <div className="login-card">
                    <div className="login-logo">MindCare AI</div>
                    <div className="login-sub">AI-Based Mental Healthcare Prediction System</div>

                    <div className="role-tog">
                        <button type="button" className={`role-btn ${role === 'patient' ? 'active' : ''}`} onClick={() => { setRole('patient'); setIsRegistering(false); clearAllInputs(); }}>
                            <i className="ti ti-user"></i> Patient
                        </button>
                        <button type="button" className={`role-btn ${role === 'clinician' ? 'active' : ''}`} onClick={() => { setRole('clinician'); setIsRegistering(false); clearAllInputs(); }}>
                            <i className="ti ti-stethoscope"></i> Clinician
                        </button>
                        <button type="button" className={`role-btn ${role === 'admin' ? 'active' : ''}`} onClick={() => { setRole('admin'); setIsRegistering(false); clearAllInputs(); }}>
                            <i className="ti ti-shield-check"></i> Admin
                        </button>
                    </div>

                    {/* noValidate waxaa loo kadday si uu u ogolaado JS handling xata hadii field dhimanyahay */}
                    <form onSubmit={handleAuth} noValidate autoComplete="off" key={isRegistering ? 'reg' : 'login'}>
                        {isRegistering && (
                            <>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <div className="fg" style={{ flex: 1 }}>
                                        <label className="fl">First Name</label>
                                        <input className="fi" type="text" value={fName} onChange={e => setFName(e.target.value)} />
                                    </div>
                                    <div className="fg" style={{ flex: 1 }}>
                                        <label className="fl">Middle Name</label>
                                        <input className="fi" type="text" value={mName} onChange={e => setMName(e.target.value)} />
                                    </div>
                                </div>
                                <div className="fg">
                                    <label className="fl">Last Name</label>
                                    <input className="fi" type="text" value={lName} onChange={e => setLName(e.target.value)} />
                                </div>
                                {role === 'clinician' && (
                                    <div className="fg">
                                        <label className="fl">Specialisation</label>
                                        <input className="fi" type="text" value={specialisation} onChange={e => setSpecialisation(e.target.value)} placeholder="e.g. Psychiatry" />
                                    </div>
                                )}
                            </>
                        )}

                        <div className="fg">
                            <label className="fl">Email address</label>
                            <input className="fi" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
                        </div>

                        <div className="fg">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <label className="fl">Password</label>
                                {!isRegistering && (
                                    <button type="button" className="btn btn-ghost btn-sm" style={{ fontSize: '11px', padding: 0 }} onClick={() => { setIsRegistering(false); setIsForgotPass(true); clearAllInputs(); }}>
                                        Forgot Password?
                                    </button>
                                )}
                            </div>
                            <input className="fi" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password" />
                        </div>

                        {isRegistering && (
                            <div className="fg" style={{ marginBottom: '12px' }}>
                                <label className="fl">Confirm Password</label>
                                <input className="fi" type="password" value={confirmPass} onChange={e => setConfirmPass(e.target.value)} placeholder="Confirm your password" />
                            </div>
                        )}

                        <button type="submit" className="btn btn-pri btn-lg btn-block" style={{ marginTop: '16px' }}>
                            {isRegistering ? 'Create Account' : 'Sign in'} <i className="ti ti-arrow-right"></i>
                        </button>

                        {role !== 'admin' && (
                            <div style={{ marginTop: '12px', textAlign: 'center' }}>
                                <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setIsRegistering(!isRegistering); clearAllInputs(); }}>
                                    {isRegistering ? 'Back to Login' : 'Create new account'}
                                </button>
                            </div>
                        )}
                    </form>
                </div>
            </div>
        </div>
    );
}
