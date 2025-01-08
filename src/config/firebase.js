// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyDw_ZWqOlmncDSJ4WvnF2MhIanT0rAV7Mc",
    authDomain: "my-app-8dc05.firebaseapp.com",
    databaseURL: "https://my-app-8dc05-default-rtdb.firebaseio.com",
    projectId: "my-app-8dc05",
    storageBucket: "my-app-8dc05.firebasestorage.app",
    messagingSenderId: "829542615689",
    appId: "1:829542615689:web:e5d868b61ac88395811458",
    measurementId: "G-GND9DMK2D8"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);