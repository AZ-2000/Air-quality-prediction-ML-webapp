// // src/components/ParticlesBackground.jsx
// import React from "react";
// import Particles from "react-tsparticles";
// import { loadFull } from "tsparticles";

// export default function ParticlesBackground() {
//   const particlesInit = async (main) => {
//     await loadFull(main);
//   };

//   return (
//     <Particles
//       id="tsparticles"
//       init={particlesInit}
//       options={{
//         fullScreen: {
//           enable: true,
//           zIndex: -1
//         },
//         background: {
//           color: {
//             value: "#000", // or use 'transparent'
//           },
//         },
//         particles: {
//           number: {
//             value: 50,
//             density: {
//               enable: true,
//               area: 800,
//             },
//           },
//           color: {
//             value: "#ffffff",
//           },
//           links: {
//             enable: true,
//             color: "#ffffff",
//             distance: 150,
//             opacity: 0.4,
//             width: 1,
//           },
//           move: {
//             enable: true,
//             speed: 2,
//           },
//         },
//       }}
//     />
//   );
// }
