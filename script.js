/* =========================================
   1. 加载页面控制 (Preloader Logic)
========================================= */
window.addEventListener('load', () => {
    const preloader = document.getElementById('preloader');
    
    if (preloader) {
        // 关键修改：用 setTimeout 强制等待 3.5 秒 (3500毫秒) 后再开始淡出动画
        // 这样即使网页瞬间加载完了，这个画面也会停留 3.5 秒
        setTimeout(() => {
            preloader.classList.add('fade-out');
            
            // 再等 1.5 秒 (等 CSS 里的 opacity 动画播完) 后，把元素彻底隐藏
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 1500); 
            
        }, 3500); // 你可以调整这个数字，3500 = 3.5秒，5000 = 5秒
    }
});

/* =========================================
   2. 数据读取与交互 (Data & Interaction)
   使用 DOMContentLoaded 确保 HTML 骨架搭好后就开始去拿 JSON 数据
========================================= */
document.addEventListener('DOMContentLoaded', () => {
    
    // 读取外部的 JSON 数据
    fetch('data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应出错，找不到 JSON 文件');
            }
            return response.json();
        })
        .then(data => {
            console.log("🎉 JSON 数据加载成功！");
            console.log("项目名称: " + data.projectName);
            console.log("导演: " + data.director.name);
        })
        .catch(error => {
            console.error('读取 JSON 时发生错误:', error);
        });

});

// 1. 准备物品的数据仓库 (增加了 sourceUrl 和 csvFile 字段)
const itemsData = {
    1: {
        title: "1987 Taiwan Cinema Manifesto",
        category: "Manifesto",
        desc: "An original draft of the The 1987 'Taiwan Cinema Manifesto' is a foundational document co-signed by Edward Yang and fellow visionary filmmakers. This bold declaration demanded a 'New Cinema' that prioritized cultural identity and artistic integrity over commercial exploitation, screenplay, showcasing Yang's meticulous notes on character dialogue and urban alienation.",
        img: "images/item1_big.jpg",
        sourceUrl: "https://www.twreporter.org/a/saturday-features-film-interview-jan-hung-tze", 
        csvFile: "data/item1.csv" 
    },
    2: {
        title: "Atom Films",
        category: "Organization",
        desc: "An independent production entity founded by Edward Yang in 1992. This entity served as the operational core during his 'Independent Exploration' period.",
        img: "images/item2_big.jpg",
        sourceUrl: "https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do?disj=19D8F5E6C1E0A7CE09CFC6CADDAB9A88&fhl=zh_TW",
        csvFile: "data/item2.csv"
    },
    3: {
        title: "Astro Boy: THE BRAVE IN SPACE",
        category: "Animation",
        desc: "A pioneering Japanese animated series directed by Osamu Tezuka. It served as a profound spiritual totem for Edward Yang, inspiring both his humanistic worldview and the naming of his independent production company, 'Atom Films'. It symbolizes his lifelong pursuit of marrying technological rationality with artistic creation.",
        img: "images/item3_big.jpg",
        sourceUrl: "https://tezukaosamu.net/en/anime/5.html",
        csvFile: "data/item3.csv"
    },
    4: {
        title: "Map of Streets in Taipei City",
        category: "Map",
        desc: "This 1985 map serves as the spatial backbone of our cinematic network. It doesn't just show roads; it provides the coordinate system for Edward Yang's narratives. Both A Confucian Confusion and Yi Yi are semantically anchored to this specific cartographic record, illustrating how the 'Maverick Engineer' utilized the rigid urban grid to frame his stories of human alienation. ",
        img: "images/item4_big.jpg",
        sourceUrl: "https://collections.nmth.gov.tw/CollectionContent.aspx?a=132&RNO=2004.003.0188#",
        csvFile: "data/item4.csv"
    },
    5: {
        title: "A Confucian Confusion",
        category: "Moving Image",
        desc: "A satirical masterpiece that dissects the ideological confusion between traditional Confucian ethics and the hyper-capitalist reality of 1990s Taipei. It marks a critical point in Yang's independent era, utilizing rapid-fire dialogue to critique modern urban life.",
        img: "images/item5_big.jpg",
        sourceUrl: "https://www.imdb.com/title/tt0109685/",
        csvFile: "data/item5.csv"
    },
    6: {
        title: "The Analects",
        category: "Book",
        desc: "An authoritative English translation by historian Annping Chin that emphasizes historical authenticity. This text forms an intertextual relationship with Yang's deconstruction of Confucian traditions in A Confucian Confusion. It reveals the ruptures and 'confusion' that arise when ancient ethics confront the modern metropolis (such as Taipei).",
        img: "images/item6_big.jpeg",
        sourceUrl: "https://archive.org/details/theanalectsconfucius/page/n37/mode/2up",
        csvFile: "data/item6.csv"
    },
    7: {
        title: "John R. Benton Hall",
        category: "Building",
        desc: "The historic seat of the College of Engineering at UF. For Edward Yang, this hall was the physical locus where his 'Western Logic' was crystallized. The rigorous pedagogical environment here provided the intellectual scaffolding for his future cinematic dissections of modern society, bridging the gap between electrical systems and social systems.",
        img: "images/item7_big.jpg",
        sourceUrl: "https://www.eng.ufl.edu/facilities/hwcoe-buildings-information/hwcoe-building-directory/name/john-r-benton-hall/",
        csvFile: "data/item7.csv"
    },
    8: {
        title: "Stage photo of 'Journey to the East 97 Beijing, Hong Kong, Taipei'",
        category: "Social documentary photography",
        desc: "In January 1997, Edward Yang participated in the 'One Table, Two Chairs' theatrical experiment in Hong Kong. This photograph captures how he translated his urban observations of Taipei into a cross-regional theatrical language, foreshadowing the globalized perspective on modern anxiety seen in his later works.",
        img: "images/item8_big.jpg",
        sourceUrl: "https://www.gettyimages.nl/detail/nieuwsfoto%27s/actors-play-a-scene-from-a-sketch-by-director-edward-yang-nieuwsfotos/2254629295?adppopup=true",
        csvFile: "data/item8.csv"
    },
    9: {
        title: "Yi Yi: A One and a Two",
        category: "Moving Image",
        desc: "Edward Yang's magnum opus which won him the Best Director award at the 53rd Cannes Film Festival. Funded by Japanese capital, this transnational co-production represents the pinnacle of his independent artistic journey. It offers a macroscopic, multi-generational observation of middle-class struggles, urban alienation, and the universal human condition in contemporary Taipei.",
        img: "images/item9_big.jpeg",
        sourceUrl: "https://www.festival-cannes.com/en/f/yi-yi-2",
        csvFile: "data/item9.csv"
    },
    10: {
        title: "Edward Yang (Contemporary Film Directors)",
        category: "Biography",
        desc: "This 2005 biography by John Anderson offers a comprehensive overview of Edward Yang's cinematic legacy. As a cornerstone of the Contemporary Film Directors collection, the book examines Yang's role as a pioneering architect of the Taiwan New Cinema.",
        img: "images/item10_big.png",
        sourceUrl: "https://archive.org/details/edwardyang00ande/mode/2up",
        csvFile: "data/item10.csv"
    },
};

// 2. 切换详情的函数
function showDetail(itemId) {
    const data = itemsData[itemId];
    if (!data) return;

    // 获取 DOM 元素 (去掉了 film 和 year，加入了 link 和 btn)
    const titleEl = document.getElementById('item-title');
    const imgEl = document.getElementById('item-img');
    const categoryEl = document.getElementById('item-category');
    const descEl = document.getElementById('item-desc');
    const sourceLinkEl = document.getElementById('item-source-link');
    const csvBtnEl = document.getElementById('item-csv-btn');

    // 填入数据
    titleEl.innerText = data.title;
    imgEl.src = data.img;
    categoryEl.innerText = data.category;
    descEl.innerText = data.desc;

    // 动态更新链接的 href (如果没有填链接，就隐藏这个按钮)
    if (data.sourceUrl) {
        sourceLinkEl.href = data.sourceUrl;
        sourceLinkEl.style.display = 'inline-block';
    } else {
        sourceLinkEl.style.display = 'none';
    }

    // 动态更新下载按钮的 href (如果没有填文件路径，就隐藏这个按钮)
    if (data.csvFile) {
        csvBtnEl.href = data.csvFile;
        csvBtnEl.style.display = 'inline-block';
    } else {
        csvBtnEl.style.display = 'none';
    }

    // 动画效果
    const content = document.querySelector('.details-content');
    content.style.opacity = 0;
    setTimeout(() => {
        content.style.transition = "opacity 0.5s ease";
        content.style.opacity = 1;
    }, 50);
}

/* =========================================
   6. 图片放大功能逻辑
========================================= */
function openModal() {
    const modal = document.getElementById("image-modal");
    const modalImg = document.getElementById("modal-img");
    const itemImg = document.getElementById("item-img");
    
    // 打开黑屏遮罩，并把详情页的图片路径传给放大镜里的图片
    modal.style.display = "block";
    modalImg.src = itemImg.src;
}

function closeModal() {
    // 关闭黑屏遮罩
    document.getElementById("image-modal").style.display = "none";
}


/* =========================================
   7. 页面加载完成后，默认显示物品 1
========================================= */
document.addEventListener('DOMContentLoaded', () => {
    // 等页面 HTML 骨架搭好，立刻触发点击第 1 个物品的逻辑
    showDetail(1);
});