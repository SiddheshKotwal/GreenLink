document.addEventListener("DOMContentLoaded", function() {

    var navbar = document.querySelector('nav');
    var faTimes = document.querySelector('.fa-times');
    var faBarsAll = document.querySelectorAll('.fa-bars');
    var faBars = document.querySelector('bars-hidden');
    var desiredPagesOut = ['/login', '/register'];
    var desiredPagesIn = ['/products', '/services', '/carbonFootprint'];
    var greenlink = document.querySelector('.head_greenlink');
    var inputs = document.querySelectorAll('input');
    var buttons = document.querySelectorAll('button');
    var labels = document.querySelectorAll('label');
    var textarea = document.querySelector('textarea');
    var mb = document.querySelectorAll('hr');

    if(window.matchMedia("(min-width: 300px) and (max-width: 1500px)").matches){
        navbar.classList.remove('navbar-index');
        faTimes.style.display = 'none';

        if(window.location.pathname === '/carbonFootprint'){
            if(window.matchMedia("(min-width: 300px) and (max-width: 600px)").matches){
                if(mb){
                    mb.forEach(function(mbTag){
                        mbTag.classList.remove('mb-4');
                        mbTag.classList.add('mb-2');
                        mbTag.classList.remove('mt-3');
                        mbTag.classList.add('mt-1');
                    });
                }
            }
            if(window.matchMedia("(min-width: 450px) and (max-width: 600px)").matches){
                if(mb){
                    mb.forEach(function(mbTag){
                        mbTag.classList.add('mb-4');
                        mbTag.classList.remove('mb-2');
                        mbTag.classList.add('mt-3');
                        mbTag.classList.remove('mt-1');
                    });
                }
            }
        }

        document.querySelectorAll('.visit').forEach(function(selector){
            selector.innerHTML = '&nbsp; visit &nbsp;';
        })

        document.querySelectorAll('.fa-bars').forEach(function(list){

            list.addEventListener('click', function(){
                navbar.classList.remove('navbar-scroll');
                navbar.classList.add('navbar-index');
                faTimes.style.display = 'inline';
                greenlink.style.display = 'none';
            })
        });

        faTimes.addEventListener('click', function(){
            navbar.classList.remove('navbar-index');
            navbar.classList.add('navbar-scroll');
            faTimes.style.display = 'none';
            greenlink.style.display = 'block';
            if(window.location.pathname === '/'){
                let scrolll = window.scrollY;

                if(scrolll < 600){
                    navbar.classList.remove('navbar-scroll');
                };
            };
        });

        if(desiredPagesOut.includes(window.location.pathname)){
            document.getElementById("logout").style.display = 'none';
            document.getElementById("logout").style.pointerEvents = 'none';
            navbar.classList.remove('navbar-index');
            greenlink.style.display = 'block';
            navbar.classList.add('navbar-scroll');
        }

        if(desiredPagesIn.includes(window.location.pathname)){
            navbar.classList.remove('navbar-index');
            navbar.classList.add('navbar-scroll');
            greenlink.style.display = 'block';
        }

        if(window.matchMedia("(min-width: 300px) and (max-width: 800px)").matches){
            if(inputs){
                inputs.forEach(function(input){
                    input.classList.add('form-control-sm');
                });
            }
        }

        if(textarea){
            textarea.classList.add('form-control-sm');
        }
        
        if(buttons){
            buttons.forEach(function(button){
                button.classList.add('btn-sm');
            });
        }

        if(labels){
            labels.forEach(function(label){
                label.classList.add('col-form-label-sm');
            });
        }

    }
    else {
        faTimes.style.display = 'none';
        if(faBarsAll){
            faBarsAll.forEach(function(bar){
                bar.style.display = 'none';
            });
        }

        if(inputs){
            inputs.forEach(function(input){
                input.classList.remove('form-control-sm');
            });
        }

        if(textarea){
            textarea.classList.remove('form-control-sm');
        }
        
        if(buttons){
            buttons.forEach(function(button){
                button.classList.remove('btn-sm');
            });
        }

        if(labels){
            labels.forEach(function(label){
                label.classList.remove('col-form-label-sm');
            });
        }

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
    }

    // Check if the current page is the homepage (URL '/')
    if (window.location.pathname === '/') {

        window.addEventListener('scroll', function() {
            var scroll = window.scrollY;

            if (window.matchMedia('(min-width: 1500px)').matches){
                if (scroll > 600) {
                    navbar.classList.remove('navbar-index');
                    navbar.classList.add('navbar-scroll');
                } else {
                    navbar.classList.remove('navbar-scroll');
                    navbar.classList.add('navbar-index');
                }
            }
            else if(this.window.matchMedia('(min-width: 300px) and (max-width: 1500px)').matches){
                if (scroll > 600){
                    navbar.classList.add('navbar-scroll');
                    if(faBars){
                        faBars.style.display = 'block';
                    }
                    document.querySelector('.head_greenlink').style.display = 'block';
                    if(navbar.classList.contains('navbar-index')){
                        navbar.classList.remove('navbar-scroll');
                        greenlink.style.display = 'none';
                    }
                }
                else{
                    navbar.classList.remove('navbar-scroll');
                    document.querySelector('nav > a').style.display = 'none';
                }
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
            document.querySelector('.carbon').style.display = 'block';
        }, 1000);
    };

    hideAlert();

    function hideAlert() {
        var alertElement = document.querySelector('.Alert');
        var carbonFootprint = document.querySelector('.carbon');
        if (alertElement) {
            setTimeout(function() {
                alertElement.style.display = 'none';
                alertElement.innerHTML = '';
            }, 5000);
        }
        else if(carbonFootprint){
            setTimeout(function(){
                carbonFootprint.style.display = 'none';
                carbonFootprint.innerHTML = '';
            }, 15000);
        }
    }

    let tabLinks = document.querySelectorAll('.nav-tabs .nav-link');
    let calImages = document.getElementById('calculator-images');

    tabLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            if (this.href.includes('#house')) {
                calImages.src = 'https://saveonenergy.ca/-/media/Images/SaveOnEnergy/residential/net-zero-home-disocver-home-2.ashx?h=1000&w=1500&la=en&hash=80056C97F2F57E41F1336E183039E6D3';
            } else if (this.href.includes('#transport')) {
                calImages.src = 'https://images.unsplash.com/photo-1669334788758-c97e6263f149?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1135&q=80';
            } else if (this.href.includes('#air-transport')) {
                calImages.src = 'https://images.unsplash.com/photo-1566827346655-6ad4e69dd3f9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1240&q=80';
            } else if (this.href.includes('#other')) {
                calImages.src = 'https://vir.com.vn/stores/news_dataimages/dinhthuy/062020/18/17/in_article/tetra-pak-commits-to-net-zero-emissions.jpg';
            }
        });
    });
});
    
