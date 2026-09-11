const viewer = document.querySelector('.model-viewer');
const mount = viewer.querySelector('.model-canvas');
const cover = viewer.querySelector('.model-cover');
const status = viewer.querySelector('.model-status');
const loadButton = viewer.querySelector('.load-model');
const zh = viewer.dataset.language === 'zh';

loadButton.addEventListener('click', async () => {
  loadButton.disabled = true;
  status.textContent = zh ? '正在准备三维预览…' : 'Preparing the 3D preview…';
  viewer.dataset.state = 'loading';
  let renderer;
  let decoder;
  let controls;
  let environmentTarget;
  try {
    const [THREE, { OrbitControls }, { GLTFLoader }, { DRACOLoader }, { RoomEnvironment }] = await Promise.all([
      import('three'), import('three/addons/controls/OrbitControls.js'),
      import('three/addons/loaders/GLTFLoader.js'), import('three/addons/loaders/DRACOLoader.js'),
      import('three/addons/environments/RoomEnvironment.js'),
    ]);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.domElement.setAttribute('aria-label', zh ? '三维空间模型' : '3D space model');
    mount.append(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#f2f6fb');
    const environment = new RoomEnvironment();
    const pmrem = new THREE.PMREMGenerator(renderer);
    environmentTarget = pmrem.fromScene(environment, 0.04);
    scene.environment = environmentTarget.texture;
    environment.dispose();
    pmrem.dispose();
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8496ad, 1));
    const sun = new THREE.DirectionalLight(0xffffff, 2);
    sun.position.set(5, 12, 8);
    scene.add(sun);

    const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 1000);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.maxPolarAngle = Math.PI / 2 - 0.01;
    controls.cursorStyle = 'grab';
    controls.listenToKeyEvents(mount);
    const render = () => renderer.render(scene, camera);
    controls.addEventListener('change', render);

    decoder = new DRACOLoader();
    decoder.setDecoderPath(new URL('../vendor/three/examples/jsm/libs/draco/gltf/', import.meta.url).href);
    decoder.setWorkerLimit(2);
    const loader = new GLTFLoader().setDRACOLoader(decoder);
    const gltf = await loader.loadAsync(viewer.dataset.modelSrc, (event) => {
      const progress = event.total ? `${Math.round(event.loaded / event.total * 100)}%` : `${(event.loaded / 1e6).toFixed(1)} MB`;
      status.textContent = zh ? `正在加载模型 ${progress}，随后解码贴图…` : `Loading model ${progress}, then decoding textures…`;
    });
    decoder.dispose();
    const bounds = new THREE.Box3().setFromObject(gltf.scene);
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const radius = size.length() / 2;
    gltf.scene.position.sub(center);
    scene.add(gltf.scene);
    camera.near = radius / 1000;
    camera.far = radius * 50;
    controls.minDistance = radius * 0.08;
    controls.maxDistance = radius * 8;
    controls.target.set(0, 0, 0);
    let plan = false;
    const fit = () => {
      const distance = radius / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) / Math.min(camera.aspect, 1) * 1.1;
      camera.position.copy(new THREE.Vector3(...(plan ? [0, 1, 0.001] : [0.75, 1.05, 1])).normalize().multiplyScalar(distance));
      controls.target.set(0, 0, 0);
      controls.update();
      render();
    };
    const resize = () => {
      const width = mount.clientWidth;
      const height = mount.clientHeight;
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      render();
    };
    new ResizeObserver(resize).observe(mount);
    resize();
    fit();
    cover.hidden = true;
    viewer.querySelector('.model-tools').hidden = false;
    viewer.dataset.state = 'ready';
    status.textContent = zh ? '拖动旋转 · 滚轮缩放 · 右键或方向键平移' : 'Drag to orbit · Scroll to zoom · Right-drag or arrow keys to pan';
    viewer.querySelector('.reset-model').addEventListener('click', () => { plan = false; fit(); });
    viewer.querySelector('.plan-model').addEventListener('click', () => { plan = true; fit(); });
    const fullscreen = viewer.querySelector('.fullscreen-model');
    fullscreen.hidden = !document.fullscreenEnabled;
    fullscreen.addEventListener('click', async () => {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await viewer.requestFullscreen();
      } catch (error) {
        status.textContent = zh ? '无法进入全屏，请继续在页面内查看。' : 'Full screen is unavailable; you can keep exploring here.';
        console.error('Fullscreen request failed:', error);
      }
    });
  } catch (error) {
    decoder?.dispose();
    controls?.dispose();
    environmentTarget?.dispose();
    renderer?.dispose();
    mount.replaceChildren();
    viewer.dataset.state = 'error';
    status.textContent = zh ? '模型未能加载，请检查网络及浏览器的 WebGL 支持后重试。' : 'The model could not load. Check your connection and browser WebGL support, then retry.';
    loadButton.disabled = false;
    console.error('Space preview failed to load:', error);
  }
});
