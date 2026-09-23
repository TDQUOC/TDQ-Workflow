/**
 * TDQ Workflow plugin for OpenCode.
 *
 * Why this file is JavaScript in a Python repo: OpenCode registers plugins through a
 * programmatic API, not a manifest. Every other host TDQ supports reads a JSON manifest that
 * points at `./skills/`, so this is the one adapter that has to be code. It is also the only
 * place in the repo that needs Node at run time — a limit the user set explicitly, together
 * with the rule this file obeys: NO npm package, standard library only.
 *
 * It reads the SAME `skills/` directory every other host reads. Nothing is copied: the whole
 * point of the adapter model is that there is one source, and `path.resolve(__dirname,
 * '../../skills')` is what keeps it that way.
 *
 * Dual generation, like the host itself:
 *   V1 — named export `TdqWorkflowPlugin`, used as the server hook.
 *   V2 — default export `{ id, setup }`, read by the plugin supervisor.
 *
 * Every step is wrapped. A plugin that throws during activation takes down the WHOLE plugin
 * generation on this host, provider plugins included, which leaves the user with no models at
 * all. Degrading quietly — one skill skipped, or no bootstrap — always beats that.
 *
 * Log service: on by default to stderr with an ISO timestamp, muted with TDQ_LOG=0.
 */

import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** The one source every host points at. Never a copy. */
export const THU_MUC_SKILL = path.resolve(__dirname, '../../skills');

const MA_PLUGIN = 'tdq-workflow';
const SKILL_MO_DAU = 'tdq-intake';

function logBat() {
  return process.env.TDQ_LOG !== '0';
}

function log(thongDiep) {
  if (!logBat()) return;
  const moc = new Date().toISOString().replace(/\.\d+Z$/, '');
  console.error(`[${moc}] ${MA_PLUGIN}: ${thongDiep}`);
}

/**
 * Tách frontmatter YAML tối giản: đủ cho `name` và `description`, không hơn.
 *
 * Cố tình KHÔNG kéo một parser YAML về: hai trường này là tất cả những gì host cần, còn một
 * package npm ở đây là phá đúng giới hạn đã đặt cho adapter. Xử lý `\r?\n` vì repo được checkout
 * trên Windows với CRLF.
 */
export function tachFrontmatter(vanBan) {
  const khop = vanBan.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!khop) return { frontmatter: {}, than: vanBan };

  const frontmatter = {};
  let khoaCuoi = null;
  for (const dongTho of khop[1].split('\n')) {
    const dong = dongTho.replace(/\r$/, '');
    const viTri = dong.indexOf(':');
    if (viTri > 0 && !/^\s/.test(dong)) {
      const khoa = dong.slice(0, viTri).trim();
      const giaTri = dong.slice(viTri + 1).trim();
      // `|` và `>` là dấu mở khối, bản thân chúng không mang giá trị.
      frontmatter[khoa] = /^(\||>)[+-]?$/.test(giaTri) ? '' : giaTri;
      khoaCuoi = khoa;
    } else if (khoaCuoi !== null && dong.trim() !== '') {
      frontmatter[khoaCuoi] = `${frontmatter[khoaCuoi]} ${dong.trim()}`.trim();
    }
  }
  for (const khoa of Object.keys(frontmatter)) {
    frontmatter[khoa] = frontmatter[khoa].replace(/^['"]|['"]$/g, '');
  }
  return { frontmatter, than: khop[2] };
}

/**
 * Đọc mọi skill trong nguồn chung. Trả [] khi thư mục không có — không ném.
 *
 * Được export để test gọi thẳng: một adapter chỉ chạy đúng bên trong host thì không có cách nào
 * kiểm được trước khi phát hành.
 */
export function docSkill(thuMuc = THU_MUC_SKILL) {
  let muc;
  try {
    muc = fs.readdirSync(thuMuc, { withFileTypes: true });
  } catch (loi) {
    log(`không đọc được ${thuMuc}: ${loi.message}`);
    return [];
  }

  const ra = [];
  for (const e of muc) {
    if (!e.isDirectory()) continue;
    const duong = path.join(thuMuc, e.name, 'SKILL.md');
    let vanBan;
    try {
      vanBan = fs.readFileSync(duong, 'utf8');
    } catch {
      continue;  // thư mục không phải skill — bỏ qua, không phải lỗi
    }
    const { frontmatter, than } = tachFrontmatter(vanBan);
    ra.push({
      id: e.name,
      name: frontmatter.name || e.name,
      ...(frontmatter.description ? { description: frontmatter.description } : {}),
      path: duong,
      content: than,
    });
  }
  return ra;
}

/** Dòng mở đầu chèn vào phiên: chỉ trỏ đường, không chép luật. */
export function moDauPhien(danhSach = docSkill()) {
  const coIntake = danhSach.some((s) => s.id === SKILL_MO_DAU);
  if (!coIntake) return '';
  return [
    '<TDQ_WORKFLOW>',
    'Mọi yêu cầu mới đều mở bằng skill `tdq-intake`, kể cả câu hỏi nhỏ.',
    'Quy trình: intake → spec → plan → implement → QC → report. Hai cổng duyệt là spec và plan;',
    'cấm sửa code ngoài `docs/` khi chưa có duyệt. Ghi state CHỈ qua `scripts/tdq_state.py`.',
    '</TDQ_WORKFLOW>',
  ].join('\n');
}

async function dangKySkill(ctx, danhSach) {
  if (!ctx?.skill?.transform) return 0;
  let dem = 0;
  await ctx.skill.transform((draft) => {
    for (const skill of danhSach) {
      try {
        draft.add(skill);
        dem += 1;
      } catch (loi) {
        // Host từ chối một skill thì bỏ đúng skill đó. Để lỗi thoát ra khỏi callback này là
        // host tắt cứng cả plugin, mất luôn phần chèn context.
        log(`host từ chối skill "${skill.id}": ${loi.message}`);
      }
    }
  });
  return dem;
}

async function chenMoDau(ctx, moDau) {
  if (!moDau || typeof ctx?.session?.hook !== 'function') return;
  await ctx.session.hook('context', async (suKien) => {
    try {
      const tin = suKien?.messages;
      if (!Array.isArray(tin) || tin.length === 0) return;
      const dauTien = tin.find((m) => m.role === 'user');
      if (!dauTien || !Array.isArray(dauTien.content)) return;
      const daCo = dauTien.content.some(
        (p) => p.type === 'text' && typeof p.text === 'string' && p.text.includes('<TDQ_WORKFLOW>'),
      );
      if (daCo) return;
      dauTien.content.unshift({ type: 'text', text: moDau });
    } catch (loi) {
      log(`hook context lỗi: ${loi.message}`);
    }
  });
}

/** V2 — plugin supervisor gọi hàm này. */
export async function setup(ctx) {
  const danhSach = docSkill();
  try {
    const dem = await dangKySkill(ctx, danhSach);
    log(`đăng ký ${dem}/${danhSach.length} skill từ ${THU_MUC_SKILL}`);
  } catch (loi) {
    log(`đăng ký skill thất bại: ${loi.message}`);
  }
  try {
    await chenMoDau(ctx, moDauPhien(danhSach));
  } catch (loi) {
    log(`gắn hook context thất bại: ${loi.message}`);
  }
}

/** V1 — host đọc named export này. */
export const TdqWorkflowPlugin = async (ctx) => {
  const danhSach = docSkill();
  return {
    config: async (cauHinh) => {
      try {
        cauHinh.skills = [...(cauHinh.skills || []), ...danhSach];
      } catch (loi) {
        log(`ghi cấu hình skill thất bại: ${loi.message}`);
      }
      return cauHinh;
    },
  };
};

export default {
  id: MA_PLUGIN,
  server: TdqWorkflowPlugin,
  setup,
  docSkill,
  moDauPhien,
  tachFrontmatter,
};
