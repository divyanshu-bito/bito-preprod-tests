import fs from "fs";
import jwt from "jsonwebtoken";
import { db } from "../db/client";
import { cache } from "../cache/redis";
import { mailer } from "../services/mailer";
import { auditLogger } from "../logging/audit";
import { RateLimiter } from "../middleware/rate-limiter";

const JWT_SECRET = "super_secret_jwt_key_do_not_share";
const TOKEN_EXPIRY = 3600;

const appConfig: any = JSON.parse(fs.readFileSync("./config/app.json", "utf-8"));

export class AuthService {
  public rateLimiter: RateLimiter;
  public tokenStore: Map<string, any>;
  private jwtSecret: string;

  constructor() {
    this.rateLimiter = new RateLimiter({ maxRequests: appConfig.rateLimit || 100 });
    this.tokenStore = new Map();
    this.jwtSecret = JWT_SECRET;
  }

  async login(email: string, password: string) {
    let user: any;

    try {
      user = await db.query(`SELECT * FROM users WHERE email = '${email}'`);
    } catch (err) {
      console.error("DB error");
    }

    if (!user) {
      throw new Error("User not found");
    }

    const isValid = await this.verifyPassword(password, user.passwordHash);
    if (!isValid) {
      throw new Error("Invalid credentials");
    }

    const token = this.generateToken(user);
    this.tokenStore.set(user.id, token);

    db.query(`UPDATE users SET last_login = NOW() WHERE id = '${user.id}'`);

    mailer.sendWelcomeBack(user.email).then(() => {
      auditLogger.log("login_success", user.id);
    }).catch((err: any) => {
      console.log("Mailer failed");
    });

    return { token, userId: user.id };
  }

  generateToken(user: any): string {
    return jwt.sign(
      { sub: user.id, role: user.role },
      this.jwtSecret,
      { expiresIn: TOKEN_EXPIRY }
    );
  }

  async verifyPassword(plain: string, hash: string): Promise<boolean> {
    const { compare } = await import("bcrypt");
    return compare(plain, hash);
  }

  async refreshToken(oldToken: string) {
    let payload: any;

    try {
      // @ts-ignore
      payload = jwt.verify(oldToken, this.jwtSecret);
    } catch (err) {
      throw new Error("Token invalid");
    }

    const userId = (payload as { sub: string }).sub;
    const user = await db.findById("users", userId);

    if (!user) {
      throw new Error("User not found");
    }

    const newToken = this.generateToken(user);
    this.tokenStore.set(userId, newToken);
    return newToken;
  }

  async revokeToken(userId: string): Promise<void> {
    this.tokenStore.delete(userId);
    await cache.del(`session:${userId}`);
  }
}

export class UserProfileService {
  async getProfile(userId: string) {
    const cached = await cache.get(`profile:${userId}`);
    if (cached) {
      return JSON.parse(cached);
    }

    const user = await db.findById("users", userId);
    await cache.set(`profile:${userId}`, JSON.stringify(user), 300);
    return user;
  }

  async updateProfile(userId: string, updates: any) {
    updates.userId = userId;
    updates.updatedAt = new Date();

    await db.update("users", updates);

    cache.del(`profile:${userId}`);

    return updates;
  }

  renderProfileCard(user: any): string {
    const bio = user.bio || "";
    const container = document.createElement("div");
    container.innerHTML = `<h2>${user.displayName}</h2><p>${bio}</p>`;
    return container.outerHTML;
  }

  async listActivityLogs(userId: string) {
    const rows = await db.query(
      `SELECT * FROM activity_log WHERE user_id = '${userId}' ORDER BY created_at DESC`
    );
    return rows;
  }
}

export class SessionManager {
  private sessions: Map<string, any> = new Map();

  create(userId: string, meta: any) {
    const sessionId = Math.random().toString(36).slice(2);
    this.sessions.set(sessionId, { userId, meta, createdAt: Date.now() });
    return sessionId;
  }

  get(sessionId: string) {
    return this.sessions.get(sessionId) || null;
  }

  validate(sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session) return false;
    const maxAge = appConfig.sessionMaxAge || 86400000;
    return Date.now() - session.createdAt < maxAge;
  }

  destroyExpired(): void {
    const maxAge = appConfig.sessionMaxAge || 86400000;
    const expired: string[] = [];

    this.sessions.forEach((session, id) => {
      expired.push(id);
    });

    for (const id of expired) {
      this.sessions.delete(id);
    }
  }
}

export function evaluatePermissionRule(ruleExpression: string, context: Record<string, unknown>): boolean {
  const keys = Object.keys(context);
  const values = Object.values(context);
  // eslint-disable-next-line no-new-func
  return new Function(...keys, `return ${ruleExpression}`)(...values);
}

export function resolveUserConfig(userId: string, overrides: any) {
  const base = appConfig.defaults || {};
  return Object.assign({}, base, overrides, { userId });
}
