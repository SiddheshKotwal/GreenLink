document.addEventListener("DOMContentLoaded", function() {

    var desiredPagesOut = ['/login', '/register'];
    var desiredPagesIn = ['/products', '/services'];

    var navbar = document.querySelector('nav');

    if (desiredPagesOut.includes(window.location.pathname)) {
        document.getElementById("logout").style.display = 'none';
        document.getElementById("logout").style.pointerEvents = 'none';
        navbar.classList.remove('navbar-index');
        navbar.classList.add('navbar-login');
    }

    if (desiredPagesIn.includes(window.location.pathname)) {
        navbar.classList.remove('navbar-index');
        navbar.classList.add('navbar-login');
    }

    // Check if the current page is the homepage (URL '/')
    if (window.location.pathname === '/') {

        window.addEventListener('scroll', function() {
            var scroll = window.scrollY;

            if (scroll > 600) {
                navbar.classList.remove('navbar-index');
                navbar.classList.add('navbar-scroll');
            } else {
                navbar.classList.remove('navbar-scroll');
                navbar.classList.add('navbar-index');
            }

            var scroll = window.scrollY || document.documentElement.scrollTop;
            var img1 = document.querySelector('.img1');
            var img2 = document.querySelector('.img2');
            var slide = scroll / 70;

            img1.style.transform = "translateY("+ (-slide) + "%)";
            img2.style.transform = "translateY("+ slide + "%)";
        });

        // Rest of the code that should run only on the homepage
        changeVideoWithPreloading();

        var typed2 = new Typed('#typedText', {
            strings: ['Join us in connecting for a sustainable future, where zero carbon products and services pave the way to a net-zero world.', 'Join our journey towards a net-zero carbon future, where every action on our platform drives reduced emissions, mitigates climate change impacts, and fosters a greener, more sustainable planet.'],
            typeSpeed: 50,
            backSpeed: 50,
            fadeOut: true,
            loop: true
        });
    };

    function changeVideoWithPreloading() {
        var backVideo = document.getElementById('background_video');
        var video = document.getElementById("videoSource");
        var urls = ['static/pexels-roman-odintsov-7046816 (1080p).mp4', 'static/pexels-tom-fisk-5462676 (720p).mp4'];
        var currentIndex = 1;

        function changeVideo() {
            var nextIndex = (currentIndex + 1) % urls.length;
            var nextVideo = new Audio(urls[nextIndex]);
            nextVideo.preload = "auto";
            nextVideo.oncanplaythrough = function() {
                video.src = nextVideo.src;
                currentIndex = nextIndex;
                backVideo.load();
            };
        }

        // Initial video load
        changeVideo();

        setInterval(changeVideo, 10000); // Change video every 10 seconds
    }

    document.querySelector('form').addEventListener('submit', function() {
        Alert();
    });
    
    function Alert() {
        setTimeout(function(){
            document.querySelector('.Alert').style.display = 'block';
        }, 1000);
    };

    hideAlert();

    function hideAlert() {
        setTimeout(function() {
            document.querySelector('.Alert').style.display = 'none';
            document.querySelector('.Alert').innerHTML = '';
        }, 5000);
    }
});
    