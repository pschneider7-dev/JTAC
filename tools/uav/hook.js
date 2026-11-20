  /* --- UAV-Generator: nur in der Arbeitskopie, nicht in der App --- */
  window.__uav = (function(){
    var FL = (typeof ACTIVE !== 'undefined') ? function(){ return ACTIVE; } : function(){ return FEATS; };
    var TX = (typeof tx === 'function') ? tx : function(x){ return (x && typeof x === 'object' && !Array.isArray(x)) ? x.def : x; };
    var RL = (typeof rayList !== 'undefined') ? rayList : [];
    var ground = null, bushes = [], W = 960, H = 720;
    function rnd(s){ return function(){ s = (s*16807) % 2147483647; return (s - 1)/2147483646; }; }
    function tex(kind, seed){
      var c = document.createElement('canvas'); c.width = c.height = 1024; var x = c.getContext('2d'), r = rnd(seed), i;
      var P = {grass:['#55613a','#4a5632','#626b42','#3f4a2b','#6d6a48'], mud:['#5e5240','#4f4535','#6b5e49','#463d30','#736650'],
               dry:['#8a7f5d','#7b7152','#958a68','#6e6649','#a09572'], snow:['#d9dcdc','#c9cdcd','#e6e8e8','#b9bcba','#9da09c'],
               therm:['#2b2b2b','#262626','#303030','#222222','#353535']}[kind];
      x.fillStyle = P[0]; x.fillRect(0, 0, 1024, 1024);
      for(i = 0; i < 2600; i++){ x.globalAlpha = 0.10 + r()*0.25; x.fillStyle = P[1 + Math.floor(r()*4)]; var s = 4 + r()*46; x.beginPath(); x.ellipse(r()*1024, r()*1024, s, s*(0.4 + r()*0.8), r()*3.14, 0, 6.29); x.fill(); }
      for(i = 0; i < 9000; i++){ x.globalAlpha = 0.25 + r()*0.4; x.fillStyle = P[1 + Math.floor(r()*4)]; x.fillRect(r()*1024, r()*1024, 1 + r()*3, 1 + r()*3); }
      x.globalAlpha = kind === 'therm' ? 0.25 : 0.35; x.strokeStyle = kind === 'snow' ? '#8f918c' : kind === 'therm' ? '#3c3c3c' : '#3a3326'; x.lineWidth = 14;
      for(i = 0; i < 3; i++){ var y0 = r()*1024, a = (r() - 0.5)*0.6; [0, 52].forEach(function(o){ x.beginPath(); x.moveTo(-20, y0 + o); x.bezierCurveTo(300, y0 + o + 300*a, 700, y0 + o - 200*a, 1044, y0 + o + 100*a); x.stroke(); }); }
      var t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(10, 10); t.encoding = T.sRGBEncoding; t.anisotropy = 8; return t;
    }
    function setGround(kind, seed){
      if(!ground){ ground = new T.Mesh(new T.PlaneGeometry(220, 220), new T.MeshStandardMaterial({roughness:1, metalness:0})); ground.rotation.x = -Math.PI/2; ground.position.y = -0.004; ground.receiveShadow = true; scene.add(ground); }
      ground.material.map = tex(kind, seed); ground.material.color.set(kind === 'therm' ? '#ffffff' : '#ffffff'); ground.material.needsUpdate = true;
      if(typeof grid !== 'undefined' && grid) grid.visible = false;
      bushes.forEach(function(b){ scene.remove(b); }); bushes = [];
      if(kind !== 'snow'){ var r = rnd(seed + 7), n = 3 + Math.floor(r()*5), i, j;
        var col = new T.Color(kind === 'therm' ? '#2e2e2e' : (kind === 'dry' ? '#4d4a2c' : kind === 'mud' ? '#3b4128' : '#2c3820')).convertSRGBToLinear();
        for(i = 0; i < n; i++){ var a = r()*6.28, d = 7.5 + r()*14, g = new T.Group(); g.position.set(Math.cos(a)*d, 0, Math.sin(a)*d);
          for(j = 0; j < 4 + Math.floor(r()*5); j++){ var s = 0.35 + r()*0.8, b = new T.Mesh(new T.IcosahedronGeometry(s, 1), new T.MeshStandardMaterial({color:col, roughness:1, flatShading:true}));
            b.scale.y = 0.6 + r()*0.3; b.position.set((r() - 0.5)*1.8, s*0.45, (r() - 0.5)*1.8); b.castShadow = true; g.add(b); }
          scene.add(g); bushes.push(g); } }
    }
    function shot(o){
      renderer.setPixelRatio(1); renderer.setSize(W, H, false); camera.aspect = W/H; camera.updateProjectionMatrix();
      var D = Math.PI/180; cam.az = o.az*D; cam.el = o.el*D; cam.r = o.r; cam.t.copy(CENTER); cam.t.x += o.dx || 0; cam.t.z += o.dz || 0;
      placeCamera(); scene.updateMatrixWorld(true); renderer.render(scene, camera);
      var url = renderer.domElement.toDataURL('image/png');
      var pins = [], v = new T.Vector3(), dir = new T.Vector3(), ray = new T.Raycaster();
      FL().forEach(function(f){
        if(!f.anchor) return; f.anchor.getWorldPosition(v); var w = v.clone(); v.project(camera);
        var px = (v.x*0.5 + 0.5)*100, py = (-v.y*0.5 + 0.5)*100;
        dir.copy(w).sub(camera.position); var dist = dir.length(); dir.multiplyScalar(1/dist);
        ray.set(camera.position, dir); ray.near = 0; ray.far = Math.max(0.1, dist - 0.14);
        var occ = RL.length ? ray.intersectObjects(RL, false).length > 0 : false;
        pins.push({id:f.id, x:+px.toFixed(1), y:+py.toFixed(1), occ:occ, n:TX(f.n), s:TX(f.s)});
      });
      return {url:url, pins:pins};
    }
    function sprite(o){
      if(ground) ground.visible = false; bushes.forEach(function(b){ b.visible = false; });
      if(typeof grid !== 'undefined' && grid) grid.visible = false;
      turret.visible = !o.noTurret;
      var Wd = o.w || 960, Hd = o.h || 720;
      renderer.setPixelRatio(1); renderer.setSize(Wd, Hd, false); camera.aspect = Wd/Hd; camera.updateProjectionMatrix();
      var D = Math.PI/180; cam.az = o.az*D; cam.el = o.el*D; cam.r = o.r; cam.t.copy(CENTER);
      placeCamera(); scene.updateMatrixWorld(true); renderer.render(scene, camera);
      var url = renderer.domElement.toDataURL('image/png');
      function proj(v){ var p = v.clone().project(camera); return [(p.x*0.5 + 0.5)*Wd, (-p.y*0.5 + 0.5)*Hd]; }
      var bow = null; FL().forEach(function(f){ if((f.id === 'bow' || f.id === 'bug') && f.anchor){ var w = new T.Vector3(); f.anchor.getWorldPosition(w); bow = proj(w); } });
      var hb = new T.Box3().setFromObject(hull), c = hb.getCenter(new T.Vector3());
      turret.visible = true;
      return {url:url, center:proj(c), bow:bow, hullLen:+(hb.max.x - hb.min.x).toFixed(2), hullW:+(hb.max.z - hb.min.z).toFixed(2)};
    }
    return {setGround:setGround, shot:shot, sprite:sprite, mode:function(m){ setMode(m); }};
  })();
