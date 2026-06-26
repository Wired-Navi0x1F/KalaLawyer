// Three.js Interactive Particle Constellation Network (Light Theme)
document.addEventListener("DOMContentLoaded", function () {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas) return;

  const container = canvas.parentElement;

  // Scene setup
  const scene = new THREE.Scene();

  // Camera setup
  const camera = new THREE.PerspectiveCamera(
    60,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  );
  camera.position.z = 80;

  // Renderer setup
  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    alpha: true, // Transparent background
    antialias: true
  });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // Particle configuration
  const particleCount = 80; // Slightly fewer particles for cleaner light appearance
  const particles = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const velocities = [];

  // Seed positions and velocities
  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 120;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 80;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 60;

    velocities.push({
      x: (Math.random() - 0.5) * 0.1,
      y: (Math.random() - 0.5) * 0.1,
      z: (Math.random() - 0.5) * 0.08
    });
  }

  particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  // Create point cloud material programmatically via HTML Canvas
  const canvasDot = document.createElement('canvas');
  canvasDot.width = 16;
  canvasDot.height = 16;
  const ctx = canvasDot.getContext('2d');
  const grad = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
  // Warm brown color gradient
  grad.addColorStop(0, 'rgba(160, 120, 85, 1)');
  grad.addColorStop(1, 'rgba(160, 120, 85, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 16, 16);
  const dotTexture = new THREE.CanvasTexture(canvasDot);

  const particleMaterial = new THREE.PointsMaterial({
    color: 0xa07855, // Gold-brown accent
    size: 2.5,
    transparent: true,
    opacity: 0.7,
    map: dotTexture,
    blending: THREE.NormalBlending, // Normal blending for light backgrounds
    depthWrite: false
  });

  const pointCloud = new THREE.Points(particles, particleMaterial);
  scene.add(pointCloud);

  // Line connections geometry and material
  const lineMaterial = new THREE.LineBasicMaterial({
    color: 0xa07855,
    transparent: true,
    opacity: 0.15,
    blending: THREE.NormalBlending
  });

  let lineSegments;

  // Interactivity state
  let mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  const maxDistance = 22; // Distance threshold for lines

  // Handle mouse movements
  window.addEventListener('mousemove', (e) => {
    mouse.targetX = (e.clientX / window.innerWidth - 0.5) * 30;
    mouse.targetY = -(e.clientY / window.innerHeight - 0.5) * 20;
  });

  // Animation Loop
  function animate() {
    requestAnimationFrame(animate);

    // Smooth mouse parallax interpolation
    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    // Rotate point cloud slightly based on mouse
    pointCloud.rotation.y = mouse.x * 0.012;
    pointCloud.rotation.x = -mouse.y * 0.008;

    // Update particle positions
    const posArray = pointCloud.geometry.attributes.position.array;

    for (let i = 0; i < particleCount; i++) {
      const idx = i * 3;
      
      posArray[idx] += velocities[i].x;
      posArray[idx + 1] += velocities[i].y;
      posArray[idx + 2] += velocities[i].z;

      if (Math.abs(posArray[idx]) > 70) velocities[i].x *= -1;
      if (Math.abs(posArray[idx + 1]) > 50) velocities[i].y *= -1;
      if (Math.abs(posArray[idx + 2]) > 40) velocities[i].z *= -1;
    }

    pointCloud.geometry.attributes.position.needsUpdate = true;

    // Create and update line connections
    if (lineSegments) scene.remove(lineSegments);

    const linePositions = [];
    for (let i = 0; i < particleCount; i++) {
      const idx1 = i * 3;
      const x1 = posArray[idx1];
      const y1 = posArray[idx1 + 1];
      const z1 = posArray[idx1 + 2];

      for (let j = i + 1; j < particleCount; j++) {
        const idx2 = j * 3;
        const x2 = posArray[idx2];
        const y2 = posArray[idx2 + 1];
        const z2 = posArray[idx2 + 2];

        const dist = Math.sqrt(
          (x1 - x2) ** 2 +
          (y1 - y2) ** 2 +
          (z1 - z2) ** 2
        );

        if (dist < maxDistance) {
          linePositions.push(x1, y1, z1);
          linePositions.push(x2, y2, z2);
        }
      }
    }

    if (linePositions.length > 0) {
      const lineGeometry = new THREE.BufferGeometry();
      lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
      lineSegments = new THREE.LineSegments(lineGeometry, lineMaterial);
      scene.add(lineSegments);
    }

    renderer.render(scene, camera);
  }

  animate();

  window.addEventListener("resize", onWindowResize);

  function onWindowResize() {
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    
    renderer.setSize(width, height);
  }
});
